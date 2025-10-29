# Copyright 2024 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Literal, Optional

import azure.cognitiveservices.speech as speechsdk
from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    llm,
    utils,
)

from .. import models
from ..log import logger
from . import utils as realtime_utils


@dataclass
class _LiveInterpreterOptions:
    """Internal configuration options for Live Interpreter"""

    subscription_key: str
    region: str
    target_languages: list[str]
    use_personal_voice: bool
    speaker_profile_id: Optional[str]
    sample_rate: int
    enable_word_level_timestamps: bool
    profanity_option: Literal["masked", "removed", "raw"]


class LiveInterpreterModel(llm.LLM):
    """
    LiveKit Agent integration for Azure Live Interpreter API.

    This provides real-time speech-to-speech translation with automatic language
    detection and personal voice preservation.

    Example:
        ```python
        from livekit.agents import AgentSession
        from livekit.plugins import azure

        session = AgentSession(
            llm=azure.realtime.LiveInterpreterModel(
                target_languages=["fr", "es"],
                use_personal_voice=True,
            )
        )
        ```
    """

    def __init__(
        self,
        *,
        target_languages: list[str],
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
        use_personal_voice: bool = True,
        speaker_profile_id: Optional[str] = None,
        sample_rate: int = 16000,
        enable_word_level_timestamps: bool = False,
        profanity_option: Literal["masked", "removed", "raw"] = "masked",
        api_connect_options: utils.http_context.APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> None:
        """
        Initialize Live Interpreter model.

        Args:
            target_languages: List of target language codes (e.g., ["fr", "es", "de"])
            subscription_key: Azure Speech subscription key (or set AZURE_SPEECH_KEY env var)
            region: Azure region (e.g., "eastus") (or set AZURE_SPEECH_REGION env var)
            use_personal_voice: Whether to use personal voice for synthesis
            speaker_profile_id: Optional speaker profile ID for personal voice
            sample_rate: Audio sample rate in Hz (16000 or 24000)
            enable_word_level_timestamps: Enable word-level timestamps
            profanity_option: How to handle profanity ("masked", "removed", "raw")
            api_connect_options: API connection options
        """
        super().__init__()

        # Get credentials from environment if not provided
        subscription_key = subscription_key or os.environ.get("AZURE_SPEECH_KEY")
        region = region or os.environ.get("AZURE_SPEECH_REGION")

        if not subscription_key:
            raise ValueError(
                "Azure Speech subscription key is required. "
                "Set AZURE_SPEECH_KEY environment variable or pass subscription_key parameter."
            )

        if not region:
            raise ValueError(
                "Azure region is required. "
                "Set AZURE_SPEECH_REGION environment variable or pass region parameter."
            )

        # Validate target languages
        invalid_langs = [
            lang for lang in target_languages
            if lang not in models.SUPPORTED_TARGET_LANGUAGES
        ]
        if invalid_langs:
            raise ValueError(
                f"Unsupported target languages: {invalid_langs}. "
                f"Supported languages: {models.SUPPORTED_TARGET_LANGUAGES}"
            )

        self._opts = _LiveInterpreterOptions(
            subscription_key=subscription_key,
            region=region,
            target_languages=target_languages,
            use_personal_voice=use_personal_voice,
            speaker_profile_id=speaker_profile_id,
            sample_rate=sample_rate,
            enable_word_level_timestamps=enable_word_level_timestamps,
            profanity_option=profanity_option,
        )
        self._api_connect_options = api_connect_options

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        fnc_ctx: Optional[llm.FunctionContext] = None,
        temperature: Optional[float] = None,
        n: int = 1,
        parallel_tool_calls: Optional[bool] = None,
    ) -> "LiveInterpreterSession":
        """
        Create a new Live Interpreter session.

        Note: Live Interpreter does not support function calling or text-based chat.
        This method is provided for LLM interface compatibility but only supports
        audio-based translation.

        Args:
            chat_ctx: Chat context (not used for Live Interpreter)
            fnc_ctx: Function context (not supported)
            temperature: Temperature (not applicable)
            n: Number of responses (not applicable)
            parallel_tool_calls: Parallel tool calls (not supported)

        Returns:
            LiveInterpreterSession for managing the translation session
        """
        if fnc_ctx is not None:
            logger.warning(
                "Live Interpreter does not support function calling. "
                "Function context will be ignored."
            )

        return LiveInterpreterSession(
            opts=self._opts,
            api_connect_options=self._api_connect_options,
        )


class LiveInterpreterSession(llm.LLMStream):
    """
    Active Live Interpreter session for real-time speech translation.

    This class manages the connection to Azure Speech Service and handles
    audio streaming, translation results, and synthesized audio output.
    """

    def __init__(
        self,
        *,
        opts: _LiveInterpreterOptions,
        api_connect_options: utils.http_context.APIConnectOptions,
    ) -> None:
        super().__init__()

        self._opts = opts
        self._api_connect_options = api_connect_options

        # Azure Speech SDK objects
        self._recognizer: Optional[speechsdk.translation.TranslationRecognizer] = None
        self._audio_stream: Optional[speechsdk.audio.PushAudioInputStream] = None

        # State management
        self._session_id: Optional[str] = None
        self._is_running = False
        self._closed = False

        # Event queue for results
        self._event_queue: asyncio.Queue[
            llm.ChatChunk | APIStatusError
        ] = asyncio.Queue()

        # Audio output buffer
        self._audio_buffer = bytearray()
        self._audio_lock = asyncio.Lock()

        # Metrics
        self._translation_count = 0
        self._start_time: Optional[float] = None

    async def __anext__(self) -> llm.ChatChunk:
        """Get next chat chunk from the session"""
        if self._closed:
            raise StopAsyncIteration

        try:
            event = await self._event_queue.get()
        except asyncio.CancelledError:
            raise StopAsyncIteration

        if isinstance(event, APIStatusError):
            raise event

        return event

    async def aclose(self) -> None:
        """Close the session and cleanup resources"""
        if self._closed:
            return

        self._closed = True

        try:
            await self._stop_recognition()
        except Exception as e:
            logger.error(f"Error stopping recognition: {e}")

        # Cleanup Azure SDK resources
        if self._recognizer:
            try:
                # Disconnect event handlers
                self._recognizer.recognizing.disconnect_all()
                self._recognizer.recognized.disconnect_all()
                self._recognizer.synthesizing.disconnect_all()
                self._recognizer.canceled.disconnect_all()
                self._recognizer.session_started.disconnect_all()
                self._recognizer.session_stopped.disconnect_all()
            except Exception as e:
                logger.debug(f"Error disconnecting handlers: {e}")

        if self._audio_stream:
            try:
                self._audio_stream.close()
            except Exception as e:
                logger.debug(f"Error closing audio stream: {e}")

        logger.info(
            f"Live Interpreter session closed. Total translations: {self._translation_count}"
        )

    async def _start_recognition(self) -> None:
        """Initialize and start the Azure Speech recognizer"""
        if self._is_running:
            return

        try:
            # Create V2 endpoint
            v2_endpoint = models.V2_ENDPOINT_TEMPLATE.format(region=self._opts.region)

            # Create translation config
            translation_config = speechsdk.translation.SpeechTranslationConfig(
                endpoint=v2_endpoint,
                subscription=self._opts.subscription_key,
            )

            # Add target languages
            for lang in self._opts.target_languages:
                translation_config.add_target_language(lang)

            # Configure personal voice
            if self._opts.use_personal_voice:
                translation_config.voice_name = "personal-voice"
                if self._opts.speaker_profile_id:
                    translation_config.set_property(
                        speechsdk.PropertyId.SpeechServiceResponse_RequestSpeakerProfileId,
                        self._opts.speaker_profile_id,
                    )

            # Configure profanity handling
            translation_config.set_profanity(
                getattr(
                    speechsdk.ProfanityOption,
                    self._opts.profanity_option.capitalize(),
                )
            )

            # Enable word-level timestamps if requested
            if self._opts.enable_word_level_timestamps:
                translation_config.request_word_level_timestamps()

            # Create auto-detect language config (open range for Live Interpreter)
            auto_detect_config = speechsdk.AutoDetectSourceLanguageConfig()

            # Create push audio stream
            audio_format = speechsdk.audio.AudioStreamFormat(
                samples_per_second=self._opts.sample_rate,
                bits_per_sample=16,
                channels=1,
            )
            self._audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)

            audio_config = speechsdk.audio.AudioConfig(stream=self._audio_stream)

            # Create recognizer
            self._recognizer = speechsdk.translation.TranslationRecognizer(
                translation_config=translation_config,
                auto_detect_source_language_config=auto_detect_config,
                audio_config=audio_config,
            )

            # Connect event handlers
            self._recognizer.recognizing.connect(self._on_recognizing)
            self._recognizer.recognized.connect(self._on_recognized)
            self._recognizer.synthesizing.connect(self._on_synthesizing)
            self._recognizer.canceled.connect(self._on_canceled)
            self._recognizer.session_started.connect(self._on_session_started)
            self._recognizer.session_stopped.connect(self._on_session_stopped)

            # Start continuous recognition
            await asyncio.get_event_loop().run_in_executor(
                None, self._recognizer.start_continuous_recognition
            )

            self._is_running = True
            self._start_time = asyncio.get_event_loop().time()

            logger.info(
                f"Live Interpreter session started. Target languages: {self._opts.target_languages}"
            )

        except Exception as e:
            logger.error(f"Failed to start Live Interpreter session: {e}")
            raise APIConnectionError(f"Failed to connect to Azure Speech Service: {e}")

    async def _stop_recognition(self) -> None:
        """Stop the recognition session"""
        if not self._is_running:
            return

        self._is_running = False

        if self._recognizer:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._recognizer.stop_continuous_recognition
                )
            except Exception as e:
                logger.debug(f"Error stopping recognition: {e}")

        if self._audio_stream:
            try:
                self._audio_stream.close()
            except Exception as e:
                logger.debug(f"Error closing stream: {e}")

    def _on_session_started(self, evt: speechsdk.SessionEventArgs) -> None:
        """Handle session started event"""
        self._session_id = evt.session_id
        logger.debug(f"Session started: {self._session_id}")

    def _on_session_stopped(self, evt: speechsdk.SessionEventArgs) -> None:
        """Handle session stopped event"""
        logger.debug(f"Session stopped: {evt.session_id}")
        self._is_running = False

    def _on_recognizing(
        self, evt: speechsdk.translation.TranslationRecognitionEventArgs
    ) -> None:
        """Handle intermediate recognition results"""
        try:
            detected_lang = evt.result.properties.get(
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult,
                "unknown",
            )

            # Note: With open range language detection, recognizing events may be limited
            logger.debug(f"Recognizing [{detected_lang}]: {evt.result.text}")

            # Create intermediate chat chunk
            # For Live Interpreter, we primarily emit text translations
            # Audio synthesis will be handled in the synthesizing event

        except Exception as e:
            logger.error(f"Error in recognizing handler: {e}")

    def _on_recognized(
        self, evt: speechsdk.translation.TranslationRecognitionEventArgs
    ) -> None:
        """Handle final recognition results"""
        try:
            if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
                detected_lang = evt.result.properties.get(
                    speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult,
                    "unknown",
                )

                source_text = evt.result.text
                translations = dict(evt.result.translations)

                self._translation_count += 1

                logger.info(f"Recognized [{detected_lang}]: {source_text}")
                for lang, translation in translations.items():
                    logger.info(f"  → [{lang}]: {translation}")

                # Create chat chunk with translation result
                # Format: source text + translations
                content = f"[{detected_lang}] {source_text}\n"
                for lang, translation in translations.items():
                    content += f"[{lang}] {translation}\n"

                chunk = llm.ChatChunk(
                    choices=[
                        llm.Choice(
                            delta=llm.ChoiceDelta(
                                role="assistant",
                                content=content.strip(),
                            ),
                            index=0,
                        )
                    ]
                )

                # Queue the result
                try:
                    self._event_queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    logger.warning("Event queue full, dropping result")

            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                logger.debug("No speech could be recognized")

        except Exception as e:
            logger.error(f"Error in recognized handler: {e}")

    def _on_synthesizing(
        self, evt: speechsdk.translation.TranslationSynthesisEventArgs
    ) -> None:
        """Handle audio synthesis events"""
        try:
            audio = evt.result.audio

            if len(audio) > 0:
                # Store audio data
                # In a full implementation, this would be streamed to the LiveKit room
                asyncio.create_task(self._handle_audio_data(audio))

                logger.debug(f"Audio synthesized: {len(audio)} bytes")

        except Exception as e:
            logger.error(f"Error in synthesizing handler: {e}")

    async def _handle_audio_data(self, audio: bytes) -> None:
        """Handle synthesized audio data"""
        async with self._audio_lock:
            self._audio_buffer.extend(audio)

        # In a full implementation, this would publish audio to the LiveKit room
        # For now, we just buffer it

    def _on_canceled(
        self, evt: speechsdk.translation.TranslationRecognitionCanceledEventArgs
    ) -> None:
        """Handle cancellation/error events"""
        logger.error(f"Translation canceled: {evt.reason}")

        if evt.reason == speechsdk.CancellationReason.Error:
            error_details = evt.error_details
            logger.error(f"Error details: {error_details}")

            # Queue error
            error = APIStatusError(
                message=f"Azure Speech Service error: {error_details}",
                status_code=500,
                request_id=self._session_id,
                body=None,
            )

            try:
                self._event_queue.put_nowait(error)
            except asyncio.QueueFull:
                logger.error("Event queue full, cannot queue error")

        self._is_running = False

    async def push_audio(self, frame: rtc.AudioFrame) -> None:
        """
        Push audio frame to the Live Interpreter for translation.

        Args:
            frame: Audio frame from LiveKit room
        """
        if not self._is_running:
            await self._start_recognition()

        if not self._audio_stream:
            logger.warning("Audio stream not initialized")
            return

        try:
            # Resample if necessary
            target_sample_rate = self._opts.sample_rate
            if frame.sample_rate != target_sample_rate:
                # Use LiveKit's resampler
                resampler = rtc.AudioResampler(
                    input_rate=frame.sample_rate,
                    output_rate=target_sample_rate,
                    num_channels=1,
                )
                frame = resampler.push(frame)

            # Convert to bytes
            audio_data = frame.data.tobytes()

            # Push to Azure stream
            await asyncio.get_event_loop().run_in_executor(
                None, self._audio_stream.write, audio_data
            )

        except Exception as e:
            logger.error(f"Error pushing audio: {e}")

    def get_audio_buffer(self) -> bytes:
        """
        Get buffered synthesized audio.

        Returns:
            Bytes of synthesized audio (WAV format)
        """
        return bytes(self._audio_buffer)

    def clear_audio_buffer(self) -> None:
        """Clear the audio buffer"""
        self._audio_buffer.clear()
