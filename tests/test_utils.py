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

"""Tests for utility functions"""

import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "livekit-plugins", "livekit-plugins-azure"))

from livekit.plugins.azure.realtime import utils


def test_validate_target_language():
    """Test language validation"""
    assert utils.validate_target_language("fr") is True
    assert utils.validate_target_language("es") is True
    assert utils.validate_target_language("zh-Hans") is True
    assert utils.validate_target_language("invalid") is False


def test_get_supported_languages():
    """Test getting supported languages list"""
    languages = utils.get_supported_languages()
    assert isinstance(languages, list)
    assert len(languages) > 0
    assert "fr" in languages


def test_format_language_code():
    """Test language code formatting"""
    assert utils.format_language_code("zh-cn") == "zh-Hans"
    assert utils.format_language_code("zh-CN") == "zh-Hans"
    assert utils.format_language_code("zh-tw") == "zh-Hant"
    assert utils.format_language_code("zh-hk") == "zh-Hant"
    assert utils.format_language_code("fr") == "fr"
    assert utils.format_language_code("es") == "es"


def test_create_v2_endpoint():
    """Test V2 endpoint creation"""
    endpoint = utils.create_v2_endpoint("eastus")
    assert endpoint == "wss://eastus.stt.speech.microsoft.com/speech/universal/v2"

    endpoint = utils.create_v2_endpoint("westus2")
    assert endpoint == "wss://westus2.stt.speech.microsoft.com/speech/universal/v2"


def test_estimate_audio_duration():
    """Test audio duration estimation"""
    # 1 second of 16kHz 16-bit mono audio
    audio_bytes = b"\x00" * (16000 * 2)  # 2 bytes per sample
    duration = utils.estimate_audio_duration(audio_bytes, sample_rate=16000)
    assert duration == pytest.approx(1.0, rel=0.01)

    # 2 seconds of 24kHz audio
    audio_bytes = b"\x00" * (24000 * 2 * 2)
    duration = utils.estimate_audio_duration(audio_bytes, sample_rate=24000)
    assert duration == pytest.approx(2.0, rel=0.01)


def test_chunk_audio():
    """Test audio chunking"""
    # Create 1 second of audio (16kHz, 16-bit)
    audio_bytes = b"\x00" * (16000 * 2)

    # Chunk into 100ms pieces
    chunks = utils.chunk_audio(audio_bytes, chunk_duration_ms=100, sample_rate=16000)

    # Should have 10 chunks (1000ms / 100ms)
    assert len(chunks) == 10

    # Each chunk should be 100ms worth of audio
    expected_chunk_size = int(16000 * 0.1 * 2)  # samples * duration * bytes_per_sample
    assert len(chunks[0]) == expected_chunk_size


def test_create_translation_chat_message():
    """Test creating chat message from translation"""
    message = utils.create_translation_chat_message(
        source_language="en-US",
        source_text="Hello world",
        translations={"fr": "Bonjour le monde", "es": "Hola mundo"},
    )

    assert message.role == "assistant"
    assert "en-US" in message.content
    assert "Hello world" in message.content
    assert "fr" in message.content
    assert "Bonjour le monde" in message.content
    assert "es" in message.content
    assert "Hola mundo" in message.content
