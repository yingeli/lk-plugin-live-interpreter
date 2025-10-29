# Azure Live Interpreter Examples

This directory contains example implementations of LiveKit agents using Azure Live Interpreter API.

## Prerequisites

1. **Azure Speech Service Subscription**
   - Create an Azure account at https://azure.microsoft.com/
   - Create a Speech Service resource
   - Get your subscription key and region

2. **Personal Voice Access**
   - Apply for access at https://aka.ms/customneural
   - Select "Personal Voice" for Question 20
   - Wait for approval (required for Live Interpreter)

3. **Environment Variables**
   ```bash
   export AZURE_SPEECH_KEY="your-subscription-key"
   export AZURE_SPEECH_REGION="eastus"  # or your region

   # Optional: for custom voice example
   export AZURE_SPEAKER_PROFILE_ID="your-profile-id"
   ```

4. **Python Dependencies**
   ```bash
   pip install livekit-plugins-azure python-dotenv
   ```

## Examples

### 1. Simple Interpreter (`simple_interpreter.py`)

Basic usage of Live Interpreter with two target languages.

**Features:**
- Translates to French and Spanish
- Uses personal voice
- 16kHz audio quality

**Run:**
```bash
python simple_interpreter.py dev
```

### 2. Multi-Language Meeting (`multi_language_meeting.py`)

Enterprise-grade interpreter for international meetings.

**Features:**
- Simultaneous translation to 8 languages
- Word-level timestamps
- Profanity filtering
- Suitable for large meetings

**Target Languages:**
- French, Spanish, German
- Simplified Chinese, Japanese, Korean
- Arabic, Russian

**Run:**
```bash
python multi_language_meeting.py dev
```

### 3. Custom Voice Interpreter (`custom_voice_interpreter.py`)

Uses a pre-trained personal voice profile.

**Features:**
- Specific speaker profile ID
- 24kHz high-quality audio
- Custom voice characteristics

**Setup:**
1. Create a speaker profile in Azure Speech Studio
2. Get the profile ID
3. Set `AZURE_SPEAKER_PROFILE_ID` environment variable

**Run:**
```bash
export AZURE_SPEAKER_PROFILE_ID="your-profile-id"
python custom_voice_interpreter.py dev
```

## Testing with LiveKit CLI

### Start the Agent

```bash
# Terminal 1: Start the agent
python simple_interpreter.py dev
```

### Join the Room

```bash
# Terminal 2: Join as a participant
livekit-cli join-room \
  --url ws://localhost:7880 \
  --api-key devkey \
  --api-secret secret \
  --room my-room \
  --identity user1
```

### Expected Behavior

1. Speak into your microphone
2. Agent automatically detects your language
3. Agent provides real-time translations in target languages
4. Translated audio plays back in your own voice style

## Supported Languages

Azure Live Interpreter supports 90+ target languages including:

- **European:** French (fr), Spanish (es), German (de), Italian (it), Portuguese (pt)
- **Asian:** Chinese (zh-Hans/zh-Hant), Japanese (ja), Korean (ko), Hindi (hi), Thai (th)
- **Middle Eastern:** Arabic (ar), Hebrew (he), Persian (fa), Turkish (tr)
- **Others:** Russian (ru), Polish (pl), Vietnamese (vi), and many more

Full list: See `livekit/plugins/azure/models.py`

## Configuration Options

### LiveInterpreterModel Parameters

```python
azure.realtime.LiveInterpreterModel(
    target_languages=["fr", "es"],      # Required: list of target languages
    subscription_key=None,               # Optional: defaults to env var
    region=None,                         # Optional: defaults to env var
    use_personal_voice=True,             # Use personal voice synthesis
    speaker_profile_id=None,             # Optional: specific profile ID
    sample_rate=16000,                   # 16000 or 24000 Hz
    enable_word_level_timestamps=False,  # Detailed timing info
    profanity_option="masked",           # "masked", "removed", or "raw"
)
```

## Troubleshooting

### "Personal Voice access required"

Apply for access at https://aka.ms/customneural and wait for approval.

### "Subscription key not found"

Set the environment variable:
```bash
export AZURE_SPEECH_KEY="your-key"
```

### "Region not supported"

Check supported regions at:
https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions

Common regions: `eastus`, `westus`, `westeurope`, `eastasia`

### Audio Quality Issues

Try these settings:
- Increase `sample_rate` to 24000
- Check microphone quality
- Verify network connection stability

### No Translation Output

- Verify target languages are in supported list
- Check Azure subscription has sufficient quota
- Review agent logs for error messages

## Production Deployment

For production use:

1. **Use Secure Credentials**
   - Store keys in Azure Key Vault or similar
   - Use managed identities when possible

2. **Monitor Usage**
   - Track translation quota
   - Monitor latency metrics
   - Set up alerts for errors

3. **Optimize Performance**
   - Limit target languages (2-3 recommended)
   - Use appropriate sample rate for use case
   - Consider regional deployment for latency

4. **Handle Errors**
   - Implement retry logic
   - Provide fallback options
   - Log all errors for debugging

## Resources

- [Azure Speech Service Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [Live Interpreter API Reference](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-translate-speech)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Personal Voice Overview](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/personal-voice-overview)

## License

Apache 2.0 - See LICENSE file
