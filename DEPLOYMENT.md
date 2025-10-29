# Deployment Guide: Azure Live Interpreter to LiveKit Cloud

This guide walks you through deploying the Azure Live Interpreter agent to LiveKit Cloud and testing it in the playground.

## Prerequisites

1. **LiveKit Cloud Account**
   - Sign up at https://cloud.livekit.io/
   - Create a project
   - Get API Key and Secret

2. **Azure Speech Service**
   - Active subscription with Personal Voice access
   - Subscription Key and Region

3. **Tools**
   - Docker (for local testing)
   - LiveKit CLI (optional but recommended)

## Deployment Methods

### Method 1: Deploy via LiveKit Cloud Dashboard (Recommended)

#### Step 1: Prepare Your Agent

1. **Package the plugin:**
```bash
cd livekit-plugins/livekit-plugins-azure
python -m build
# This creates dist/livekit-plugins-azure-0.1.0.tar.gz
```

2. **Push to GitHub (or any Git repository):**
```bash
git add .
git commit -m "Add Azure Live Interpreter plugin"
git push origin main
```

#### Step 2: Configure in LiveKit Cloud

1. **Go to LiveKit Cloud Dashboard:**
   - Navigate to https://cloud.livekit.io/
   - Select your project
   - Go to "Agents" section

2. **Create New Agent:**
   - Click "New Agent"
   - Name: `azure-realtime`
   - Description: `Real-time speech translation using Azure`

3. **Configure Source:**
   ```yaml
   # Option A: From GitHub
   source:
     type: git
     url: https://github.com/your-username/lk-plugin-realtime
     branch: main
     path: examples/multi_language_meeting.py

   # Option B: From Docker
   source:
     type: docker
     image: your-dockerhub/azure-realtime:latest
   ```

4. **Set Environment Variables:**
   ```
   AZURE_SPEECH_KEY=your-subscription-key-here
   AZURE_SPEECH_REGION=eastus
   AZURE_SPEAKER_PROFILE_ID=optional-profile-id
   ```

5. **Configure Resources:**
   - Memory: 512 MB
   - CPU: 0.5 cores
   - Replicas: 1 (auto-scale later if needed)

6. **Deploy:**
   - Click "Deploy"
   - Wait for agent to start (usually 1-2 minutes)

#### Step 3: Test in Playground

1. **Open Playground:**
   - In LiveKit Cloud dashboard, go to "Playground"
   - Or visit: https://meet.livekit.io/

2. **Connect to Your Project:**
   - Enter your LiveKit URL (e.g., `wss://your-project.livekit.cloud`)
   - Generate a token with your API Key/Secret
   - Join a room

3. **Start the Agent:**
   - The agent should automatically join the room
   - Look for "azure-realtime" participant

4. **Test Translation:**
   - Enable your microphone
   - Speak in any language
   - Agent will detect language and translate to configured languages
   - Translation appears as transcriptions and audio

### Method 2: Deploy via Docker (Self-Hosted)

#### Step 1: Build Docker Image

```bash
# Build the image
docker build -t azure-realtime:latest .

# Test locally
docker run -it --rm \
  -e AZURE_SPEECH_KEY="your-key" \
  -e AZURE_SPEECH_REGION="eastus" \
  -e LIVEKIT_URL="ws://localhost:7880" \
  -e LIVEKIT_API_KEY="devkey" \
  -e LIVEKIT_API_SECRET="secret" \
  azure-realtime:latest
```

#### Step 2: Push to Container Registry

```bash
# Tag for your registry
docker tag azure-realtime:latest \
  your-registry/azure-realtime:latest

# Push
docker push your-registry/azure-realtime:latest
```

#### Step 3: Deploy to LiveKit Cloud

```bash
# Using LiveKit CLI
livekit-cli deploy \
  --url wss://your-project.livekit.cloud \
  --api-key your-api-key \
  --api-secret your-api-secret \
  --image your-registry/azure-realtime:latest \
  --env AZURE_SPEECH_KEY=your-key \
  --env AZURE_SPEECH_REGION=eastus
```

### Method 3: Deploy via LiveKit CLI

#### Step 1: Install LiveKit CLI

```bash
# macOS
brew install livekit-cli

# Linux/Windows
# Download from https://github.com/livekit/livekit-cli/releases
```

#### Step 2: Create Deployment Config

Create `deploy.yaml`:
```yaml
apiVersion: livekit.io/v1
kind: AgentDeployment
metadata:
  name: azure-realtime
spec:
  source:
    git:
      url: https://github.com/your-username/lk-plugin-realtime
      branch: main
      path: examples/multi_language_meeting.py

  environment:
    - name: AZURE_SPEECH_KEY
      value: your-key
    - name: AZURE_SPEECH_REGION
      value: eastus

  resources:
    memory: 512Mi
    cpu: 500m

  replicas: 1
```

#### Step 3: Deploy

```bash
livekit-cli deploy apply -f deploy.yaml \
  --url wss://your-project.livekit.cloud \
  --api-key your-api-key \
  --api-secret your-api-secret
```

## Configuration Options

### Agent Configuration

Edit [agent.yaml](agent.yaml) to customize:

```yaml
# Target languages
environment:
  TARGET_LANGUAGES: "fr,es,de,zh-Hans,ja,ko,ar,ru"

# Audio quality
  SAMPLE_RATE: "24000"  # 16000 or 24000

# Personal voice
  USE_PERSONAL_VOICE: "true"
  AZURE_SPEAKER_PROFILE_ID: "optional-profile-id"

# Logging
  LOG_LEVEL: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Room Configuration

Configure which rooms the agent joins:

```python
# In multi_language_meeting.py, add room filter:
async def entrypoint(ctx: JobContext):
    # Only join rooms with specific prefix
    if not ctx.room.name.startswith("translator-"):
        return

    # Your agent code...
```

## Testing Your Deployment

### 1. Local Testing (Before Deployment)

```bash
# Test with local LiveKit server
cd examples
python multi_language_meeting.py dev

# In another terminal, join the room
livekit-cli join-room \
  --url ws://localhost:7880 \
  --api-key devkey \
  --api-secret secret \
  --room test-room \
  --identity user1
```

### 2. Cloud Testing

```bash
# Join via CLI
livekit-cli join-room \
  --url wss://your-project.livekit.cloud \
  --api-key your-api-key \
  --api-secret your-api-secret \
  --room translator-meeting \
  --identity user1

# Or use web playground
# Visit: https://meet.livekit.io/
```

### 3. Verify Agent Logs

In LiveKit Cloud Dashboard:
- Go to "Agents" → "azure-realtime"
- Click "Logs" tab
- Look for:
  ```
  INFO: Starting Multi-Language Interpreter in room: translator-meeting
  INFO: Target languages: fr, es, de, zh-Hans, ja, ko, ar, ru
  INFO: Multi-language interpreter ready
  ```

## Troubleshooting

### Agent Not Starting

**Check logs for:**
```
Error: Azure Speech Service error
```

**Solution:**
- Verify `AZURE_SPEECH_KEY` is correct
- Verify `AZURE_SPEECH_REGION` is correct
- Ensure Personal Voice access is approved

### No Translation Output

**Possible causes:**
1. Microphone not enabled
2. Audio format issues
3. Network connectivity

**Solution:**
```bash
# Check agent logs
# Look for: "Audio synthesized: X bytes"

# Test microphone
# Ensure browser permissions granted
```

### High Latency

**Optimization:**
1. Reduce target languages (2-3 recommended)
2. Use closer Azure region
3. Increase agent resources

```yaml
# In agent.yaml
resources:
  memory: 1Gi
  cpu: "1"
```

### Rate Limiting

**Error:**
```
Error: Too many requests
```

**Solution:**
- Check Azure quota limits
- Implement rate limiting in agent
- Upgrade Azure subscription tier

## Monitoring & Metrics

### LiveKit Cloud Dashboard

Monitor in real-time:
- Active sessions
- Translation count
- Error rates
- Resource usage

### Custom Metrics

Add to your agent:
```python
import logging
from prometheus_client import Counter, Histogram

# Define metrics
translations_total = Counter(
    'translations_total',
    'Total number of translations'
)

translation_duration = Histogram(
    'translation_duration_seconds',
    'Translation duration in seconds'
)

# Use in code
translations_total.inc()
with translation_duration.time():
    # Translation code
    pass
```

## Security Best Practices

### 1. Secure Credentials

```bash
# Never commit credentials
# Use environment variables or secrets manager

# In LiveKit Cloud, use secret storage:
# Dashboard → Settings → Secrets
# Add: AZURE_SPEECH_KEY
```

### 2. Network Security

```yaml
# Restrict network access
security:
  network_policy:
    ingress:
      - from:
        - podSelector:
            matchLabels:
              app: livekit
```

### 3. Authentication

```python
# Require authentication for agent rooms
async def entrypoint(ctx: JobContext):
    # Verify room has valid auth
    if not ctx.room.metadata.get("authenticated"):
        logger.warning("Unauthorized room access attempt")
        return
```

## Scaling

### Auto-scaling Configuration

```yaml
# In agent.yaml
autoscaling:
  enabled: true
  min_replicas: 1
  max_replicas: 10
  target_cpu_utilization: 70
  target_memory_utilization: 80
```

### Manual Scaling

```bash
# Scale via CLI
livekit-cli deploy scale azure-realtime --replicas 5

# Or update in dashboard
# Agents → azure-realtime → Scale → Set replicas
```

## Cost Optimization

### Azure Costs

1. **Reduce target languages**: 2-3 instead of 8
2. **Use 16kHz audio**: Instead of 24kHz
3. **Disable personal voice**: For lower costs

```python
# Cost-optimized configuration
azure.realtime.LiveInterpreterModel(
    target_languages=["fr", "es"],  # Only 2 languages
    use_personal_voice=False,        # Standard voices
    sample_rate=16000,               # Lower quality
)
```

### LiveKit Costs

1. **Optimize resources**: Don't over-provision
2. **Auto-scaling**: Scale down when idle
3. **Session limits**: Set max duration

```yaml
resources:
  memory: 256Mi  # Minimum needed
  cpu: "0.25"    # Minimum needed

autoscaling:
  enabled: true
  min_replicas: 0  # Scale to zero when idle
```

## Production Checklist

- [ ] Azure credentials configured
- [ ] Personal Voice access approved
- [ ] Agent deployed successfully
- [ ] Tested in playground
- [ ] Logs monitoring setup
- [ ] Error alerting configured
- [ ] Auto-scaling enabled
- [ ] Security best practices applied
- [ ] Cost monitoring enabled
- [ ] Documentation updated

## Support

- **LiveKit Docs**: https://docs.livekit.io/
- **Azure Docs**: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/
- **Issues**: https://github.com/livekit/agents/issues
- **Community**: https://livekit.io/community

---

**Last Updated**: 2024-10-28
**Version**: 0.1.0
