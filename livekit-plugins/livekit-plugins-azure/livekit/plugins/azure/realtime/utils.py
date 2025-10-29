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

"""Utility functions for Azure Live Interpreter integration with LiveKit"""

from typing import Optional

from livekit.agents import llm

from .. import models


def create_translation_chat_message(
    source_language: str,
    source_text: str,
    translations: dict[str, str],
) -> llm.ChatMessage:
    """
    Create a ChatMessage from translation results.

    Args:
        source_language: Detected source language code
        source_text: Original text in source language
        translations: Dictionary of target language to translated text

    Returns:
        ChatMessage containing the translation information
    """
    content = f"Source [{source_language}]: {source_text}\n\n"
    content += "Translations:\n"
    for lang, translation in translations.items():
        content += f"  [{lang}]: {translation}\n"

    return llm.ChatMessage(
        role="assistant",
        content=content.strip(),
    )


def validate_target_language(language_code: str) -> bool:
    """
    Validate if a language code is supported for translation.

    Args:
        language_code: Language code to validate (e.g., 'fr', 'es', 'zh-Hans')

    Returns:
        True if language is supported, False otherwise
    """
    return language_code in models.SUPPORTED_TARGET_LANGUAGES


def get_supported_languages() -> list[str]:
    """
    Get list of all supported target languages.

    Returns:
        List of supported language codes
    """
    return models.SUPPORTED_TARGET_LANGUAGES.copy()


def format_language_code(language_code: str) -> str:
    """
    Format language code to standard format.

    Azure expects specific formats for some languages:
    - Use 'zh-Hans' for Simplified Chinese, not 'zh-CN'
    - Use 'zh-Hant' for Traditional Chinese, not 'zh-TW'
    - Use 'pt' for Portuguese (Brazil), 'pt-PT' for European Portuguese

    Args:
        language_code: Input language code

    Returns:
        Formatted language code
    """
    # Common mappings
    mapping = {
        "zh-cn": "zh-Hans",
        "zh-tw": "zh-Hant",
        "zh-hk": "zh-Hant",
    }

    normalized = language_code.lower()
    return mapping.get(normalized, language_code)


def create_v2_endpoint(region: str) -> str:
    """
    Create V2 endpoint URL for Live Interpreter.

    Args:
        region: Azure region (e.g., 'eastus')

    Returns:
        V2 endpoint URL
    """
    return models.V2_ENDPOINT_TEMPLATE.format(region=region)


def estimate_audio_duration(audio_bytes: bytes, sample_rate: int = 16000) -> float:
    """
    Estimate duration of audio in seconds.

    Args:
        audio_bytes: Raw audio bytes (16-bit PCM)
        sample_rate: Sample rate in Hz

    Returns:
        Estimated duration in seconds
    """
    # 16-bit = 2 bytes per sample
    bytes_per_sample = 2
    num_samples = len(audio_bytes) / bytes_per_sample
    return num_samples / sample_rate


def chunk_audio(
    audio_bytes: bytes,
    chunk_duration_ms: int = 100,
    sample_rate: int = 16000,
) -> list[bytes]:
    """
    Split audio into chunks of specified duration.

    Args:
        audio_bytes: Raw audio bytes (16-bit PCM mono)
        chunk_duration_ms: Chunk duration in milliseconds
        sample_rate: Sample rate in Hz

    Returns:
        List of audio chunks
    """
    bytes_per_sample = 2  # 16-bit
    samples_per_chunk = int(sample_rate * chunk_duration_ms / 1000)
    bytes_per_chunk = samples_per_chunk * bytes_per_sample

    chunks = []
    for i in range(0, len(audio_bytes), bytes_per_chunk):
        chunk = audio_bytes[i : i + bytes_per_chunk]
        chunks.append(chunk)

    return chunks
