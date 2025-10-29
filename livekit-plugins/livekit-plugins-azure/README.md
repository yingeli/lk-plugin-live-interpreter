# LiveKit Azure AI Services Plugin

Official LiveKit Agent plugin for Azure AI Services, including support for Azure Live Interpreter API.

## Features

- **Live Interpreter (Preview)**: Real-time speech-to-speech translation with automatic language detection
- **Personal Voice**: Preserve speaker's style and tone across translations
- **Multi-language Support**: Translate to 90+ target languages simultaneously
- **Low Latency**: Optimized for real-time communication scenarios

## Installation

```bash
pip install livekit-plugins-azure
```

## Quick Start

### Basic Live Interpreter Agent

```python
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es"],  # French and Spanish
            use_personal_voice=True,
        )
    )

    await session.start(room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

## Configuration

Set your Azure credentials as environment variables:

```bash
export AZURE_SPEECH_KEY="your-subscription-key"
export AZURE_SPEECH_REGION="eastus"
```

## Requirements

- Azure AI Speech Service subscription
- Personal Voice access (apply at https://aka.ms/customneural)
- Python 3.9+

## Documentation

For detailed documentation, visit [LiveKit Agents Documentation](https://docs.livekit.io/agents/).

## License

Apache 2.0
