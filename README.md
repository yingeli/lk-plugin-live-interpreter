# LiveKit Azure Live Interpreter Plugin

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Official LiveKit Agent plugin for **Azure Live Interpreter API** - Real-time speech-to-speech translation with personal voice preservation.

## Features

🌐 **Automatic Language Detection** - No need to specify source language
🎤 **Personal Voice** - Preserves speaker's style and tone across translations
🔄 **Real-time Translation** - Low-latency speech-to-speech translation
🌍 **90+ Languages** - Translate to multiple languages simultaneously
🎯 **LiveKit Integration** - Seamless integration with LiveKit Agents framework
⚡ **Production Ready** - Built on Azure's enterprise-grade infrastructure

## Quick Start

### Installation

```bash
cd livekit-plugins/livekit-plugins-azure
pip install -e .
```

### Basic Usage

```python
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es", "de"],  # French, Spanish, German
            use_personal_voice=True,
        )
    )
    await session.start(room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### Environment Setup

```bash
export AZURE_SPEECH_KEY="your-subscription-key"
export AZURE_SPEECH_REGION="eastus"
```

## Architecture

This plugin integrates Azure Live Interpreter API with LiveKit Agents, providing:

```
┌─────────────────┐
│  LiveKit Room   │
│   (Audio In)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  LiveInterpreterModel       │
│  - Audio streaming          │
│  - Language detection       │
│  - Translation coordination │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Azure Speech Service V2     │
│  - Auto language detection   │
│  - Speech recognition        │
│  - Translation engine        │
│  - Personal voice synthesis  │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────┐
│  LiveKit Room   │
│  (Translations) │
└─────────────────┘
```

## Examples

See [examples/](examples/) directory for complete examples:

- **simple_interpreter.py** - Basic two-language translation
- **multi_language_meeting.py** - Enterprise conference interpreter
- **custom_voice_interpreter.py** - Using personal voice profiles

## Deployment

### Deploy to LiveKit Cloud

```bash
# Quick deployment
./deploy.sh build
./deploy.sh test

# Deploy to cloud (see DEPLOYMENT.md for details)
./deploy.sh deploy
```

**📖 Detailed Guides:**
- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Playground Guide](PLAYGROUND_GUIDE.md) - Test in LiveKit playground
- [Docker Configuration](Dockerfile) - Container setup
- [Cloud Config](cloud-deploy.yaml) - LiveKit Cloud configuration

### Test in Playground

1. Deploy agent to LiveKit Cloud
2. Visit https://meet.livekit.io/
3. Connect to your project
4. Start speaking - instant translation!

See [PLAYGROUND_GUIDE.md](PLAYGROUND_GUIDE.md) for step-by-step instructions.

## Requirements

### Azure Prerequisites

1. **Azure Account** - Sign up at https://azure.microsoft.com/
2. **Speech Service Resource** - Create in Azure Portal
3. **Personal Voice Access** - Apply at https://aka.ms/customneural (required)

### Python Requirements

- Python 3.9 or higher
- LiveKit Agents SDK 0.8.0+
- Azure Cognitive Services Speech SDK 1.40.0+

## Documentation

### Plugin Documentation
- [Plugin README](livekit-plugins/livekit-plugins-azure/README.md) - Plugin API reference
- [Architecture](ARCHITECTURE.md) - Technical architecture details
- [Examples README](examples/README.md) - Example usage guide

### Deployment Documentation
- [Deployment Guide](DEPLOYMENT.md) - Deploy to LiveKit Cloud
- [Playground Guide](PLAYGROUND_GUIDE.md) - Test in playground
- [Quick Start](QUICKSTART.md) - 5-minute setup guide

### External Resources
- [Azure Live Interpreter Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-translate-speech)
- [LiveKit Agents Docs](https://docs.livekit.io/agents/)

## License

Apache 2.0 - See [LICENSE](LICENSE) file for details.