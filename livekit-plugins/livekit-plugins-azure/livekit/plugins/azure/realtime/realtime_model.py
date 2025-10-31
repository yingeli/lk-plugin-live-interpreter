from __future__ import annotations

import asyncio
import audioop
import contextlib
import io
import os
import time
import wave
import weakref
from dataclasses import dataclass, field
from typing import Literal, Optional

import azure.cognitiveservices.speech as speechsdk
from livekit import rtc
from livekit.agents import APIConnectionError, llm, utils
from livekit.agents.types import NOT_GIVEN, NotGivenOr
from livekit.agents.metrics import RealtimeModelMetrics
from livekit.agents.metrics.base import Metadata

from .. import models
from ..log import logger
from . import utils as realtime_utils


_AUDIO_CHUNK_MS = 20


@dataclass
class _LiveInterpreterOptions:
    subscription_key: str
    region: str
    target_languages: list[str]
    use_personal_voice: bool
    speaker_profile_id: Optional[str]
    sample_rate: int
    enable_word_level_timestamps: bool
    profanity_option: Literal["masked", "removed", "raw"]


@dataclass
class _GenerationState:
    response_id: str
    message_ch: utils.aio.Chan[llm.MessageGeneration]
    function_ch: utils.aio.Chan[llm.FunctionCall]
    text_ch: utils.aio.Chan[str]
    audio_ch: utils.aio.Chan[rtc.AudioFrame]
    modalities: asyncio.Future[list[Literal["text", "audio"]]]
    created_at: float
    first_token_at: float | None = None
    completed_at: float | None = None
    output_text: list[str] = field(default_factory=list)
    text_done: bool = False
    audio_done: bool = False
    audio_expected: bool = True


class LiveInterpreterModel(llm.RealtimeModel):
    """Live Interpreter integration backed by Azure Speech Service."""

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
    ) -> None:
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

        invalid = [lang for lang in target_languages if lang not in models.SUPPORTED_TARGET_LANGUAGES]
        if invalid:
            raise ValueError(
                "Unsupported target languages: {invalid}. Supported values are documented in "
                "livekit.plugins.azure.models.SUPPORTED_TARGET_LANGUAGES".format(invalid=invalid)
            )

        super().__init__(
            capabilities=llm.RealtimeCapabilities(
                message_truncation=False,
                turn_detection=False,
                user_transcription=True,
                auto_tool_reply_generation=False,
                audio_output=use_personal_voice,
                manual_function_calls=False,
            )
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

        self._sessions = weakref.WeakSet[LiveInterpreterSession]()
        self._label = f"azure.live_interpreter.{region}"

    @property
    def model(self) -> str:
        return "azure/live-interpreter"

    @property
    def provider(self) -> str:
        return "azure"

    def session(self) -> "LiveInterpreterSession":
        sess = LiveInterpreterSession(self)
        self._sessions.add(sess)
        return sess

    async def aclose(self) -> None:
        await asyncio.gather(*(sess.aclose() for sess in list(self._sessions)), return_exceptions=True)

    def update_options(
        self,
        *,
        target_languages: Optional[list[str]] = None,
        use_personal_voice: Optional[bool] = None,
        speaker_profile_id: Optional[str] = None,
    ) -> None:
        if target_languages is not None:
            invalid = [lang for lang in target_languages if lang not in models.SUPPORTED_TARGET_LANGUAGES]
            if invalid:
                raise ValueError(
                    "Unsupported target languages: {invalid}.".format(invalid=invalid)
                )
            self._opts.target_languages = target_languages

        if use_personal_voice is not None:
            self._opts.use_personal_voice = use_personal_voice
            self._capabilities.audio_output = use_personal_voice

        if speaker_profile_id is not None:
            self._opts.speaker_profile_id = speaker_profile_id

        for sess in list(self._sessions):
            sess.update_model_options(
                target_languages=self._opts.target_languages,
                use_personal_voice=self._opts.use_personal_voice,
                speaker_profile_id=self._opts.speaker_profile_id,
            )


class LiveInterpreterSession(llm.RealtimeSession):
    def __init__(self, realtime_model: LiveInterpreterModel) -> None:
        super().__init__(realtime_model)
        self._realtime_model = realtime_model
        self._opts = realtime_model._opts

        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.get_event_loop_policy().get_event_loop()

        self._tools = llm.ToolContext.empty()
        self._chat_ctx = llm.ChatContext.empty()

        self._recognizer: Optional[speechsdk.translation.TranslationRecognizer] = None
        self._audio_stream: Optional[speechsdk.audio.PushAudioInputStream] = None
        self._input_resampler: Optional[rtc.AudioResampler] = None
        self._resampler_input_rate: Optional[int] = None
        self._resampler_input_channels: Optional[int] = None

        self._is_running = False
        self._session_id: Optional[str] = None

        self._current_generation: Optional[_GenerationState] = None
        self._pending_generation_fut: Optional[asyncio.Future[llm.GenerationCreatedEvent]] = None

        self._shutdown = asyncio.Event()

    # ------------------------------------------------------------------
    # Properties and configuration updates
    # ------------------------------------------------------------------
    @property
    def chat_ctx(self) -> llm.ChatContext:
        return self._chat_ctx.copy()

    @property
    def tools(self) -> llm.ToolContext:
        return self._tools.copy()

    def update_options(
        self,
        *,
        tool_choice: llm.ToolChoice | None = None,
        target_languages: Optional[list[str]] = None,
        use_personal_voice: Optional[bool] = None,
        speaker_profile_id: Optional[str] = None,
    ) -> None:
        if tool_choice is not None:
            logger.warning("Live Interpreter does not support tool choice updates. Ignoring request.")

        needs_restart = False

        if target_languages is not None and target_languages != self._opts.target_languages:
            self._opts.target_languages = target_languages
            needs_restart = True

        if use_personal_voice is not None and use_personal_voice != self._opts.use_personal_voice:
            self._opts.use_personal_voice = use_personal_voice
            needs_restart = True

        if speaker_profile_id is not None and speaker_profile_id != self._opts.speaker_profile_id:
            self._opts.speaker_profile_id = speaker_profile_id
            needs_restart = True

        if needs_restart:
            asyncio.create_task(self._restart_recognition())

    def update_model_options(
        self,
        *,
        target_languages: list[str],
        use_personal_voice: bool,
        speaker_profile_id: Optional[str],
    ) -> None:
        self.update_options(
            target_languages=target_languages,
            use_personal_voice=use_personal_voice,
            speaker_profile_id=speaker_profile_id,
        )

    async def update_instructions(self, instructions: str) -> None:
        logger.warning("Live Interpreter does not support runtime instructions. Ignoring update.")

    async def update_chat_ctx(self, chat_ctx: llm.ChatContext) -> None:
        self._chat_ctx = chat_ctx.copy()

    async def update_tools(self, tools: list[llm.FunctionTool | llm.RawFunctionTool]) -> None:
        if tools:
            logger.warning("Live Interpreter does not support tool calls. Ignoring provided tools.")
        self._tools = llm.ToolContext.empty()

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    async def aclose(self) -> None:
        self._shutdown.set()
        await self._stop_recognition()

        if self._pending_generation_fut and not self._pending_generation_fut.done():
            self._pending_generation_fut.cancel()
        self._pending_generation_fut = None

        if self._current_generation:
            self._finalize_generation(interrupted=True)

    async def _restart_recognition(self) -> None:
        await self._stop_recognition()
        if self._is_running:
            return
        try:
            await self._start_recognition()
        except Exception:
            logger.exception("Failed to restart Live Interpreter session")

    async def _start_recognition(self) -> None:
        if self._is_running:
            return

        loop = asyncio.get_running_loop()
        self._loop = loop

        try:
            endpoint = models.V2_ENDPOINT_TEMPLATE.format(region=self._opts.region)

            translation_config = speechsdk.translation.SpeechTranslationConfig(
                endpoint=endpoint,
                subscription=self._opts.subscription_key,
            )

            for lang in self._opts.target_languages:
                translation_config.add_target_language(lang)

            if self._opts.use_personal_voice:
                translation_config.voice_name = "personal-voice"
                if self._opts.speaker_profile_id:
                    translation_config.set_property(
                        speechsdk.PropertyId.SpeechServiceResponse_RequestSpeakerProfileId,
                        self._opts.speaker_profile_id,
                    )

            translation_config.set_profanity(
                getattr(speechsdk.ProfanityOption, self._opts.profanity_option.capitalize())
            )

            if self._opts.enable_word_level_timestamps:
                translation_config.request_word_level_timestamps()

            auto_detect_config = speechsdk.AutoDetectSourceLanguageConfig()

            audio_format = speechsdk.audio.AudioStreamFormat(
                samples_per_second=self._opts.sample_rate,
                bits_per_sample=16,
                channels=1,
            )
            self._audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)
            audio_config = speechsdk.audio.AudioConfig(stream=self._audio_stream)

            self._recognizer = speechsdk.translation.TranslationRecognizer(
                translation_config=translation_config,
                auto_detect_source_language_config=auto_detect_config,
                audio_config=audio_config,
            )

            self._recognizer.recognizing.connect(self._on_recognizing)
            self._recognizer.recognized.connect(self._on_recognized)
            self._recognizer.synthesizing.connect(self._on_synthesizing)
            self._recognizer.canceled.connect(self._on_canceled)
            self._recognizer.session_started.connect(self._on_session_started)
            self._recognizer.session_stopped.connect(self._on_session_stopped)

            await loop.run_in_executor(None, self._recognizer.start_continuous_recognition)
            self._is_running = True
            logger.info(
                "Live Interpreter session started with targets %s",
                self._opts.target_languages,
            )
        except Exception as exc:  # pragma: no cover - SDK level errors
            logger.exception("Failed to start Live Interpreter session")
            raise APIConnectionError(f"Failed to connect to Azure Speech Service: {exc}")

    async def _stop_recognition(self) -> None:
        if not self._is_running:
            return

        self._is_running = False

        if self._recognizer:
            try:
                await asyncio.get_running_loop().run_in_executor(
                    None, self._recognizer.stop_continuous_recognition
                )
            except Exception:  # pragma: no cover - best effort
                logger.debug("Error stopping Live Interpreter recognizer", exc_info=True)

            with contextlib.suppress(Exception):
                self._recognizer.recognizing.disconnect_all()
                self._recognizer.recognized.disconnect_all()
                self._recognizer.synthesizing.disconnect_all()
                self._recognizer.canceled.disconnect_all()
                self._recognizer.session_started.disconnect_all()
                self._recognizer.session_stopped.disconnect_all()

            self._recognizer = None

        if self._audio_stream:
            with contextlib.suppress(Exception):
                self._audio_stream.close()
            self._audio_stream = None

        self._input_resampler = None
        self._resampler_input_rate = None
        self._resampler_input_channels = None

    # ------------------------------------------------------------------
    # Required realtime session interface
    # ------------------------------------------------------------------
    def push_audio(self, frame: rtc.AudioFrame) -> None:
        asyncio.create_task(self._push_audio_async(frame))

    async def _push_audio_async(self, frame: rtc.AudioFrame) -> None:
        if self._shutdown.is_set():
            return

        if not self._is_running:
            await self._start_recognition()

        if not self._audio_stream:
            logger.warning("Audio stream not initialized for Live Interpreter")
            return

        try:
            data = frame.data.tobytes()
            channels = frame.num_channels

            if channels > 1:
                data = audioop.tomono(data, 2, 0.5, 0.5)
                channels = 1

            samples_per_channel = len(data) // (2 * channels)

            if frame.sample_rate != self._opts.sample_rate:
                if (
                    self._input_resampler is None
                    or self._resampler_input_rate != frame.sample_rate
                    or self._resampler_input_channels != channels
                ):
                    self._input_resampler = rtc.AudioResampler(
                        input_rate=frame.sample_rate,
                        output_rate=self._opts.sample_rate,
                        num_channels=channels,
                    )
                    self._resampler_input_rate = frame.sample_rate
                    self._resampler_input_channels = channels

                input_frame = rtc.AudioFrame(data, frame.sample_rate, channels, samples_per_channel)
                for resampled in self._input_resampler.push(input_frame):
                    self._audio_stream.write(resampled.data.tobytes())
            else:
                self._audio_stream.write(data)
        except Exception:  # pragma: no cover - SDK level exceptions
            logger.exception("Failed to push audio to Live Interpreter")

    def push_video(self, frame: rtc.VideoFrame) -> None:
        logger.debug("Live Interpreter does not accept video input. Ignoring frame.")

    def generate_reply(
        self,
        *,
        instructions: NotGivenOr[str] = NOT_GIVEN,
    ) -> asyncio.Future[llm.GenerationCreatedEvent]:
        if instructions is not NOT_GIVEN:
            logger.warning("Live Interpreter ignores ad-hoc instructions passed to generate_reply().")

        if self._pending_generation_fut and not self._pending_generation_fut.done():
            self._pending_generation_fut.cancel("Superseded by new generate_reply call")

        fut: asyncio.Future[llm.GenerationCreatedEvent] = asyncio.Future()
        self._pending_generation_fut = fut

        def _on_timeout() -> None:
            if fut.done():
                return
            fut.set_exception(llm.RealtimeError("generate_reply timed out waiting for generation"))
            if self._pending_generation_fut is fut:
                self._pending_generation_fut = None

        handle = self._loop.call_later(15.0, _on_timeout)
        fut.add_done_callback(lambda _: handle.cancel())
        return fut

    def commit_audio(self) -> None:
        # Azure continuously consumes audio; no explicit commit is required.
        pass

    def clear_audio(self) -> None:
        # Azure SDK does not support clearing buffered audio mid-session.
        logger.debug("clear_audio called but not supported by Live Interpreter")

    def interrupt(self) -> None:
        logger.debug("interrupt called but Live Interpreter does not expose interruption controls")

    def truncate(
        self,
        *,
        message_id: str,
        modalities: list[Literal["text", "audio"]],
        audio_end_ms: int,
        audio_transcript: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        logger.warning("truncate is not supported by Live Interpreter. Ignoring request for %s", message_id)

    # ------------------------------------------------------------------
    # Azure SDK callbacks (threaded)
    # ------------------------------------------------------------------
    def _on_session_started(self, evt: speechsdk.SessionEventArgs) -> None:
        self._session_id = evt.session_id
        logger.debug("Live Interpreter session started: %s", self._session_id)

    def _on_session_stopped(self, evt: speechsdk.SessionEventArgs) -> None:
        logger.debug("Live Interpreter session stopped: %s", evt.session_id)
        self._loop.call_soon_threadsafe(self._handle_session_stopped)

    def _handle_session_stopped(self) -> None:
        self._is_running = False

    def _on_recognizing(self, evt: speechsdk.translation.TranslationRecognitionEventArgs) -> None:
        detected = evt.result.properties.get(
            speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult,
            "unknown",
        )
        logger.debug("Recognizing [%s]: %s", detected, evt.result.text)

    def _on_recognized(self, evt: speechsdk.translation.TranslationRecognitionEventArgs) -> None:
        if evt.result.reason != speechsdk.ResultReason.TranslatedSpeech:
            return

        detected = evt.result.properties.get(
            speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult,
            "unknown",
        )
        source_text = evt.result.text
        translations = dict(evt.result.translations)

        self._loop.call_soon_threadsafe(
            self._handle_final_translation, detected, source_text, translations
        )

    def _on_synthesizing(self, evt: speechsdk.translation.TranslationSynthesisEventArgs) -> None:
        audio = evt.result.audio
        self._loop.call_soon_threadsafe(self._handle_audio_chunk, audio)

    def _on_canceled(self, evt: speechsdk.translation.TranslationRecognitionCanceledEventArgs) -> None:
        reason = evt.reason
        details = evt.error_details
        self._loop.call_soon_threadsafe(self._handle_cancellation, reason, details)

    # ------------------------------------------------------------------
    # Event handlers running on the asyncio loop
    # ------------------------------------------------------------------
    def _ensure_generation(self) -> _GenerationState:
        if self._current_generation and not self._current_generation.audio_done:
            return self._current_generation

        response_id = utils.shortuuid("azure-li-")
        text_ch = utils.aio.Chan[str]()
        audio_ch = utils.aio.Chan[rtc.AudioFrame]()
        modalities: asyncio.Future[list[Literal["text", "audio"]]] = asyncio.Future()
        if self._realtime_model.capabilities.audio_output:
            modalities.set_result(["audio", "text"])
        else:
            modalities.set_result(["text"])

        message_generation = llm.MessageGeneration(
            message_id=response_id,
            text_stream=text_ch,
            audio_stream=audio_ch,
            modalities=modalities,
        )

        message_ch = utils.aio.Chan[llm.MessageGeneration]()
        message_ch.send_nowait(message_generation)

        generation = _GenerationState(
            response_id=response_id,
            message_ch=message_ch,
            function_ch=utils.aio.Chan[llm.FunctionCall](),
            text_ch=text_ch,
            audio_ch=audio_ch,
            modalities=modalities,
            created_at=time.time(),
            audio_expected=self._realtime_model.capabilities.audio_output,
        )

        self._current_generation = generation

        generation_event = llm.GenerationCreatedEvent(
            message_stream=message_ch,
            function_stream=generation.function_ch,
            user_initiated=self._pending_generation_fut is not None,
        )
        self.emit("generation_created", generation_event)

        if self._pending_generation_fut and not self._pending_generation_fut.done():
            self._pending_generation_fut.set_result(generation_event)
        self._pending_generation_fut = None

        return generation

    def _handle_audio_chunk(self, audio: bytes) -> None:
        if not self._realtime_model.capabilities.audio_output:
            return

        generation = self._ensure_generation()

        if len(audio) == 0:
            generation.audio_done = True
            if not generation.audio_ch.closed:
                generation.audio_ch.close()
            self._maybe_finalize_generation()
            return

        sample_rate, num_channels, pcm_bytes = self._decode_audio(audio)

        if num_channels > 1:
            pcm_bytes = audioop.tomono(pcm_bytes, 2, 0.5, 0.5)
            num_channels = 1

        chunk_bytes = realtime_utils.chunk_audio(
            pcm_bytes,
            chunk_duration_ms=_AUDIO_CHUNK_MS,
            sample_rate=sample_rate,
        )

        for chunk in chunk_bytes:
            if not chunk:
                continue
            frame = rtc.AudioFrame(
                data=chunk,
                sample_rate=sample_rate,
                num_channels=num_channels,
                samples_per_channel=len(chunk) // (2 * num_channels),
            )
            generation.audio_ch.send_nowait(frame)

            if generation.first_token_at is None:
                generation.first_token_at = time.time()

    def _handle_final_translation(
        self,
        source_lang: str,
        source_text: str,
        translations: dict[str, str],
    ) -> None:
        generation = self._ensure_generation()

        lines = [f"[{source_lang}] {source_text}"]
        for lang, text in translations.items():
            lines.append(f"[{lang}] {text}")

        final_text = "\n".join(lines)
        generation.output_text.append(final_text)
        generation.text_ch.send_nowait(final_text)
        generation.text_ch.close()
        generation.text_done = True
        generation.completed_at = time.time()

        self._maybe_finalize_generation()

    def _handle_cancellation(
        self,
        reason: speechsdk.CancellationReason,
        details: str | None,
    ) -> None:
        logger.error("Live Interpreter canceled: %s (%s)", reason, details)

        error = llm.RealtimeModelError(
            timestamp=time.time(),
            label=self._realtime_model.label,
            error=RuntimeError(details or "Live Interpreter canceled"),
            recoverable=True,
        )
        self.emit("error", error)

        if self._current_generation:
            self._finalize_generation(interrupted=True)

        if self._pending_generation_fut and not self._pending_generation_fut.done():
            self._pending_generation_fut.set_exception(
                llm.RealtimeError(details or "Live Interpreter canceled")
            )
            self._pending_generation_fut = None

    def _maybe_finalize_generation(self) -> None:
        generation = self._current_generation
        if not generation:
            return

        if not generation.text_done:
            return

        if generation.audio_expected and not generation.audio_done:
            return

        self._finalize_generation(interrupted=False)

    def _finalize_generation(self, interrupted: bool) -> None:
        generation = self._current_generation
        if not generation:
            return

        if not generation.text_ch.closed:
            generation.text_ch.close()
        if not generation.audio_ch.closed:
            generation.audio_ch.close()

        generation.function_ch.close()
        generation.message_ch.close()

        if generation.output_text:
            self._chat_ctx.add_message(
                role="assistant",
                content="\n\n".join(generation.output_text),
                id=generation.response_id,
            )

        created = generation.created_at
        completed = generation.completed_at or time.time()
        ttft = (
            generation.first_token_at - created
            if generation.first_token_at and generation.first_token_at >= created
            else -1
        )
        duration = completed - created

        metrics = RealtimeModelMetrics(
            timestamp=created,
            request_id=generation.response_id,
            ttft=ttft,
            duration=duration,
            cancelled=interrupted,
            label=self._realtime_model.label,
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            tokens_per_second=0,
            input_token_details=RealtimeModelMetrics.InputTokenDetails(
                audio_tokens=0,
                cached_tokens=0,
                text_tokens=0,
                cached_tokens_details=None,
                image_tokens=0,
            ),
            output_token_details=RealtimeModelMetrics.OutputTokenDetails(
                text_tokens=0,
                audio_tokens=0,
                image_tokens=0,
            ),
            metadata=Metadata(
                model_name=self._realtime_model.model,
                model_provider=self._realtime_model.provider,
            ),
        )
        self.emit("metrics_collected", metrics)

        self._current_generation = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _decode_audio(data: bytes) -> tuple[int, int, bytes]:
        if not data:
            return 16000, 1, b""

        if data[:4] != b"RIFF":
            return 16000, 1, data

        with wave.open(io.BytesIO(data), "rb") as wav:
            sample_rate = wav.getframerate()
            num_channels = wav.getnchannels()
            frames = wav.readframes(wav.getnframes())

        return sample_rate, num_channels, frames
