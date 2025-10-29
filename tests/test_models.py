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

"""Tests for data models"""

import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "livekit-plugins", "livekit-plugins-azure"))

from livekit.plugins.azure import models


def test_supported_languages():
    """Test that supported languages list is not empty"""
    assert len(models.SUPPORTED_TARGET_LANGUAGES) > 0
    assert "fr" in models.SUPPORTED_TARGET_LANGUAGES
    assert "es" in models.SUPPORTED_TARGET_LANGUAGES
    assert "zh-Hans" in models.SUPPORTED_TARGET_LANGUAGES


def test_v2_endpoint_template():
    """Test V2 endpoint template formatting"""
    endpoint = models.V2_ENDPOINT_TEMPLATE.format(region="eastus")
    assert endpoint == "wss://eastus.stt.speech.microsoft.com/speech/universal/v2"
    assert endpoint.startswith("wss://")
    assert "/speech/universal/v2" in endpoint


def test_translation_result():
    """Test TranslationResult dataclass"""
    result = models.TranslationResult(
        source_language="en-US",
        source_text="Hello world",
        translations={"fr": "Bonjour le monde", "es": "Hola mundo"},
    )

    assert result.source_language == "en-US"
    assert result.source_text == "Hello world"
    assert len(result.translations) == 2
    assert result.translations["fr"] == "Bonjour le monde"
    assert result.audio_data is None
    assert result.timestamp is None


def test_live_interpreter_config():
    """Test LiveInterpreterConfig dataclass"""
    config = models.LiveInterpreterConfig(
        subscription_key="test-key",
        region="eastus",
        target_languages=["fr", "es"],
        use_personal_voice=True,
        sample_rate=16000,
    )

    assert config.subscription_key == "test-key"
    assert config.region == "eastus"
    assert config.target_languages == ["fr", "es"]
    assert config.use_personal_voice is True
    assert config.sample_rate == 16000
    assert config.speaker_profile_id is None
    assert config.enable_word_level_timestamps is False
    assert config.profanity_option == "masked"
