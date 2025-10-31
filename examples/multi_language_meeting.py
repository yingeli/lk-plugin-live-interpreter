#!/usr/bin/env python

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

"""
Multi-Language Meeting Interpreter Example

This example demonstrates using Live Interpreter for simultaneous
translation to multiple languages in a meeting scenario.

Features:
- Automatic language detection for speaker
- Simultaneous translation to multiple target languages
- Personal voice preservation
- Real-time audio output

Requirements:
- Set AZURE_SPEECH_KEY environment variable
- Set AZURE_SPEECH_REGION environment variable
- Personal Voice access (apply at https://aka.ms/customneural)
"""

import logging
from typing import List

from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import azure

logger = logging.getLogger("multi-language-meeting")
logger.setLevel(logging.INFO)

load_dotenv()

# Configure target languages for translation
# This covers major languages commonly used in international meetings
TARGET_LANGUAGES = [
    "fr",       # French
    "es",       # Spanish
    "de",       # German
    "zh-Hans",  # Simplified Chinese
    "ja",       # Japanese
    "ko",       # Korean
    "ar",       # Arabic
    "ru",       # Russian
]


async def entrypoint(ctx: JobContext):
    """
    Entry point for multi-language meeting interpreter.

    This agent provides real-time translation to 8 different languages,
    making it suitable for large international meetings or conferences.
    """
    ctx.log_context_fields = {
        "room_name": ctx.room.name,
        "target_languages": ",".join(TARGET_LANGUAGES),
    }

    logger.info(
        f"Starting Multi-Language Interpreter in room: {ctx.room.name}"
    )
    logger.info(f"Target languages: {', '.join(TARGET_LANGUAGES)}")

    # Create the agent with LiveInterpreter model
    agent = Agent(
        instructions="You are a multi-language interpreter. Translate speech to multiple languages in real-time.",
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=TARGET_LANGUAGES,
            use_personal_voice=True,
            sample_rate=16000,
            enable_word_level_timestamps=True,  # Enable detailed timing
            profanity_option="masked",  # Mask profanity in transcripts
        ),
    )

    # Create agent session
    session = AgentSession()

    await session.start(
        agent=agent,
        room=ctx.room,
    )

    logger.info("Multi-language interpreter ready")

    # Session will remain active until the room is closed
    # No need to explicitly wait - the session handles this automatically


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Optional: specify number of workers
            # num_idle_workers=2,
        )
    )
