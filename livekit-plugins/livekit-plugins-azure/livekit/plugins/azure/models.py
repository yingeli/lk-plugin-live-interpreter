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

from dataclasses import dataclass
from typing import Literal, Optional

# Supported target languages for Azure Speech Translation
SUPPORTED_TARGET_LANGUAGES = [
    "af", "am", "ar", "as", "az", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el",
    "en", "es", "et", "eu", "fa", "fi", "fil", "fj", "fr", "ga", "gl", "gu", "he", "hi",
    "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "km", "kn", "ko", "ku",
    "ky", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "nb",
    "ne", "nl", "or", "pa", "pl", "ps", "pt", "pt-PT", "ro", "ru", "sk", "sl", "sm",
    "so", "sq", "sr-Cyrl", "sr-Latn", "sv", "sw", "ta", "te", "th", "ti", "tk", "to",
    "tr", "tt", "ty", "ug", "uk", "ur", "uz", "vi", "yua", "yue", "zh-Hans", "zh-Hant",
]


@dataclass
class TranslationResult:
    """Represents a translation result from Live Interpreter"""

    source_language: str
    """Detected source language code (e.g., 'en-US')"""

    source_text: str
    """Original text in source language"""

    translations: dict[str, str]
    """Dictionary of target language code to translated text"""

    audio_data: Optional[bytes] = None
    """Synthesized audio data (WAV format) if available"""

    timestamp: Optional[float] = None
    """Timestamp of the result"""


@dataclass
class LiveInterpreterConfig:
    """Configuration for Live Interpreter"""

    subscription_key: str
    """Azure Speech Service subscription key"""

    region: str
    """Azure region (e.g., 'eastus')"""

    target_languages: list[str]
    """List of target language codes for translation"""

    use_personal_voice: bool = True
    """Whether to use personal voice for synthesis"""

    speaker_profile_id: Optional[str] = None
    """Optional speaker profile ID for personal voice"""

    sample_rate: int = 16000
    """Audio sample rate in Hz (16000 or 24000)"""

    enable_word_level_timestamps: bool = False
    """Enable word-level timestamps in results"""

    profanity_option: Literal["masked", "removed", "raw"] = "masked"
    """How to handle profanity in transcriptions"""


# Azure Speech Service V2 endpoint template
V2_ENDPOINT_TEMPLATE = "wss://{region}.stt.speech.microsoft.com/speech/universal/v2"
