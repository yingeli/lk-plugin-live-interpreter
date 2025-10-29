# Quick Start Guide

Get up and running with Azure Live Interpreter in 5 minutes!

## Prerequisites

- Python 3.9+
- Azure account with Speech Service subscription
- Personal Voice access (required for Live Interpreter)

## Step 1: Azure Setup (5 minutes)

### 1.1 Create Speech Service Resource

1. Go to [Azure Portal](https://portal.azure.com/)
2. Click "Create a resource"
3. Search for "Speech"
4. Click "Create" → "Speech"
5. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: Create new or use existing
   - **Region**: `East US` (recommended)
   - **Name**: Choose a unique name
   - **Pricing tier**: `S0` (Standard)
6. Click "Review + Create" → "Create"
7. Wait for deployment (~1 minute)

### 1.2 Get Your Credentials

1. Go to your Speech resource
2. Click "Keys and Endpoint" in left menu
3. Copy:
   - **Key 1** (your subscription key)
   - **Location/Region** (e.g., `eastus`)

### 1.3 Apply for Personal Voice Access

1. Go to https://aka.ms/customneural
2. Fill out the form
3. **Important**: Select "Personal Voice" for Question 20
4. Submit and wait for approval (usually 1-2 business days)

## Step 2: Installation (1 minute)

```bash
# Clone the repository
git clone https://github.com/livekit/agents.git
cd agents/lk-plugin-realtime

# Install the plugin
cd livekit-plugins/livekit-plugins-azure
pip install -e .

# Install example dependencies
pip install python-dotenv
```

## Step 3: Configuration (1 minute)

```bash
# Set environment variables
export AZURE_SPEECH_KEY="your-subscription-key-here"
export AZURE_SPEECH_REGION="eastus"

# Or create .env file
cd examples
cp .env.example .env
# Edit .env and add your credentials
```

## Step 4: Run Your First Interpreter (2 minutes)

### Option A: Quick Test

```bash
cd examples
python simple_interpreter.py dev
```

This starts an agent that translates to French and Spanish.

### Option B: Multi-Language Meeting

```bash
python multi_language_meeting.py dev
```

This translates to 8 languages simultaneously!

## Step 5: Test It Out

### Using LiveKit CLI

```bash
# Terminal 1: Agent is running from Step 4

# Terminal 2: Join as a participant
livekit-cli join-room \
  --url ws://localhost:7880 \
  --api-key devkey \
  --api-secret secret \
  --room test-room \
  --identity user1
```

Now speak into your microphone and see real-time translations!

### Using LiveKit Playground

1. Go to [LiveKit Playground](https://meet.livekit.io/)
2. Enter your room details:
   - **URL**: `ws://localhost:7880`
   - **Token**: Generate using devkey/secret
   - **Room**: `test-room`
3. Join and start speaking!

## What's Happening?

```
Your Voice (any language)
    ↓
Live Interpreter detects language automatically
    ↓
Translates to configured languages (French, Spanish, etc.)
    ↓
Plays back in YOUR voice style
```

## Common Issues & Solutions

### "Personal Voice access required"

**Problem**: You haven't been approved yet
**Solution**: Wait for Azure approval or disable personal voice:

```python
LiveInterpreterModel(
    target_languages=["fr", "es"],
    use_personal_voice=False,  # Use standard voices temporarily
)
```

### "Invalid subscription key"

**Problem**: Incorrect credentials
**Solution**: Double-check your key and region:

```bash
# Verify in Azure Portal
# Keys and Endpoint → Key 1 → Copy

echo $AZURE_SPEECH_KEY     # Should show your key
echo $AZURE_SPEECH_REGION  # Should show "eastus" or your region
```

### "Connection failed"

**Problem**: Network or region issue
**Solution**:
- Check internet connection
- Verify region is supported
- Try `eastus` or `westus2`

### "No audio output"

**Problem**: Audio configuration issue
**Solution**: Check microphone permissions and audio devices

## Next Steps

### Customize Your Interpreter

Edit `examples/simple_interpreter.py`:

```python
# Change target languages
azure.realtime.LiveInterpreterModel(
    target_languages=["de", "ja", "ko"],  # German, Japanese, Korean
    use_personal_voice=True,
)
```

### Add to Your Application

```python
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import azure

async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es"],
            use_personal_voice=True,
        )
    )
    await session.start(room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### Explore Examples

Check out [examples/README.md](examples/README.md) for:
- Multi-language conference interpreter
- Custom voice profiles
- Advanced configuration options

## Production Checklist

Before deploying to production:

- [ ] Use secure credential storage (Azure Key Vault)
- [ ] Set up monitoring and alerts
- [ ] Test with expected user load
- [ ] Configure error handling
- [ ] Set up logging
- [ ] Review Azure quotas and limits
- [ ] Plan for scaling
- [ ] Test language combinations
- [ ] Verify audio quality
- [ ] Document for your team

## Get Help

- **Examples**: See [examples/](examples/) directory
- **Documentation**: Read [README.md](README.md)
- **Architecture**: Check [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: Report at [GitHub Issues](https://github.com/livekit/agents/issues)
- **Community**: Join [LiveKit Discord](https://livekit.io/community)

## Supported Languages

You can translate to 90+ languages including:

| Popular Languages | Code |
|-------------------|------|
| French | `fr` |
| Spanish | `es` |
| German | `de` |
| Italian | `it` |
| Portuguese | `pt` |
| Chinese (Simplified) | `zh-Hans` |
| Japanese | `ja` |
| Korean | `ko` |
| Arabic | `ar` |
| Russian | `ru` |

Full list in [models.py](livekit-plugins/livekit-plugins-azure/livekit/plugins/azure/models.py)

## Tips & Tricks

### Optimize for Cost

```python
# Use fewer target languages
target_languages=["fr"]  # Instead of ["fr", "es", "de", ...]

# Use 16kHz instead of 24kHz
sample_rate=16000  # Lower bandwidth = lower cost
```

### Improve Quality

```python
# Use 24kHz for better audio
sample_rate=24000

# Enable timestamps for better sync
enable_word_level_timestamps=True
```

### Debug Issues

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed logs
```

## What's Next?

Congratulations! You now have a working Live Interpreter.

Explore advanced features:
- Custom voice profiles
- Multi-participant scenarios
- Integration with your app
- Production deployment

Happy translating! 🌐🎤
