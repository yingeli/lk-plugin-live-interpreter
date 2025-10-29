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
Custom Voice Interpreter Example

This example shows how to use a specific speaker profile ID
for personal voice synthesis in Live Interpreter.

This is useful when you want to use a pre-trained personal voice
instead of the automatic personal voice feature.

Requirements:
- Set AZURE_SPEECH_KEY environment variable
- Set AZURE_SPEECH_REGION environment variable
- Set AZURE_SPEAKER_PROFILE_ID environment variable (optional)
- Personal Voice access and trained speaker profile
"""

import logging
import os

from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions, RoomOutputOptions
from livekit.plugins import azure

logger = logging.getLogger("custom-voice-interpreter")
logger.setLevel(logging.INFO)

load_dotenv()


async def entrypoint(ctx: JobContext):
    """
    Entry point for custom voice interpreter.

    Uses a specific speaker profile for personal voice synthesis.
    """
    ctx.log_context_fields = {
        "room_name": ctx.room.name,
    }

    # Get speaker profile ID from environment
    speaker_profile_id = os.environ.get("AZURE_SPEAKER_PROFILE_ID")

    if not speaker_profile_id:
        logger.warning(
            "AZURE_SPEAKER_PROFILE_ID not set. "
            "Using automatic personal voice detection instead."
        )

    logger.info(f"Starting Custom Voice Interpreter in room: {ctx.room.name}")

    if speaker_profile_id:
        logger.info(f"Using speaker profile: {speaker_profile_id}")

    # Create agent session
    session = AgentSession()

    await session.start(
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es", "de"],
            use_personal_voice=True,
            speaker_profile_id=speaker_profile_id,  # Use specific profile
            sample_rate=24000,  # Higher quality audio
            enable_word_level_timestamps=True,
        ),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            auto_subscribe=True,
        ),
        room_output_options=RoomOutputOptions(
            transcription_enabled=True,
        ),
    )

    logger.info("Custom voice interpreter ready")

    await session.wait_for_completion()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
