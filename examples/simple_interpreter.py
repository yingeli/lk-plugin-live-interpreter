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
Simple Live Interpreter Agent Example

This example demonstrates basic usage of Azure Live Interpreter API
for real-time speech translation in a LiveKit room.

Requirements:
- Set AZURE_SPEECH_KEY environment variable
- Set AZURE_SPEECH_REGION environment variable
- Apply for Personal Voice access at https://aka.ms/customneural
"""

import logging

from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import azure

# Configure logging
logger = logging.getLogger("simple-interpreter")
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()


async def entrypoint(ctx: JobContext):
    """
    Entry point for the LiveKit agent.

    This creates a simple interpreter that translates speech to French and Spanish
    in real-time, preserving the speaker's voice characteristics.
    """
    ctx.log_context_fields = {
        "room_name": ctx.room.name,
        "participant_identity": "interpreter",
    }

    logger.info(f"Starting Live Interpreter in room: {ctx.room.name}")

    # Create the agent with Live Interpreter model
    agent = Agent(
        instructions="You are a live interpreter. Translate speech to French and Spanish in real-time.",
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es"],  # French and Spanish
            use_personal_voice=True,  # Preserve speaker characteristics
            sample_rate=16000,  # 16kHz audio
        ),
    )

    # Create agent session
    session = AgentSession()

    await session.start(
        agent=agent,
        room=ctx.room,
    )

    logger.info("Live Interpreter session started successfully")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
