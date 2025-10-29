# Architecture Documentation

## Project Structure

```
lk-plugin-realtime/
├── README.md                           # Main project documentation
├── LICENSE                             # Apache 2.0 license
├── CONTRIBUTING.md                     # Contribution guidelines
├── CHANGELOG.md                        # Version history
├── ARCHITECTURE.md                     # This file
├── .gitignore                         # Git ignore patterns
│
├── livekit-plugins/
│   └── livekit-plugins-azure/         # Main plugin package
│       ├── pyproject.toml             # Package configuration
│       ├── README.md                  # Plugin documentation
│       └── livekit/
│           ├── __init__.py            # Namespace package
│           └── plugins/
│               ├── __init__.py        # Namespace package
│               └── azure/
│                   ├── __init__.py    # Package exports
│                   ├── version.py     # Version info
│                   ├── log.py         # Logging configuration
│                   ├── models.py      # Data models
│                   └── realtime/
│                       ├── __init__.py           # Module exports
│                       ├── realtime_model.py    # Core implementation
│                       └── utils.py              # Helper functions
│
├── examples/
│   ├── README.md                      # Examples documentation
│   ├── .env.example                   # Environment template
│   ├── simple_interpreter.py          # Basic example
│   ├── multi_language_meeting.py      # Advanced example
│   └── custom_voice_interpreter.py    # Custom voice example
│
└── tests/
    ├── __init__.py
    ├── test_models.py                 # Model tests
    └── test_utils.py                  # Utility tests
```

## Component Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      LiveKit Room                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │Participant │  │Participant │  │Participant │             │
│  │   (EN)     │  │   (ZH)     │  │   (ES)     │             │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘             │
│         │                │                │                    │
│         └────────────────┴────────────────┘                    │
│                          │                                     │
│                          ▼                                     │
│                ┌──────────────────┐                           │
│                │  Audio Mixing    │                           │
│                └────────┬─────────┘                           │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  LiveKit Agent                      │
        │  (livekit-plugins-azure)            │
        │                                     │
        │  ┌───────────────────────────────┐ │
        │  │  LiveInterpreterModel         │ │
        │  │  - Manages configuration      │ │
        │  │  - Creates sessions           │ │
        │  └────────────┬──────────────────┘ │
        │               │                     │
        │               ▼                     │
        │  ┌───────────────────────────────┐ │
        │  │  LiveInterpreterSession       │ │
        │  │  - Audio streaming            │ │
        │  │  - Event handling             │ │
        │  │  - State management           │ │
        │  └────────────┬──────────────────┘ │
        └───────────────┼─────────────────────┘
                        │
                        ▼
        ┌─────────────────────────────────────┐
        │  Azure Speech SDK                   │
        │  (azure-cognitiveservices-speech)   │
        │                                     │
        │  ┌───────────────────────────────┐ │
        │  │  TranslationRecognizer        │ │
        │  │  - WebSocket connection       │ │
        │  │  - Event callbacks            │ │
        │  └────────────┬──────────────────┘ │
        └───────────────┼─────────────────────┘
                        │
                        ▼
        ┌─────────────────────────────────────┐
        │  Azure Speech Service V2            │
        │  wss://[region].stt.speech...       │
        │                                     │
        │  ┌───────────────────────────────┐ │
        │  │  Language Detection           │ │
        │  │         ↓                     │ │
        │  │  Speech Recognition           │ │
        │  │         ↓                     │ │
        │  │  Translation Engine           │ │
        │  │         ↓                     │ │
        │  │  Personal Voice Synthesis     │ │
        │  └───────────────────────────────┘ │
        └─────────────────────────────────────┘
                        │
                        ▼
        ┌─────────────────────────────────────┐
        │  Translation Results                │
        │  - Source text + language           │
        │  - Translated texts (multi-lang)    │
        │  - Synthesized audio (WAV)          │
        └─────────────────────────────────────┘
```

## Core Classes

### LiveInterpreterModel

**Purpose**: Main interface for creating Live Interpreter sessions

**Key Methods**:
- `__init__()`: Initialize with configuration
- `chat()`: Create a new translation session (LLM interface compatibility)

**Key Attributes**:
- `_opts`: Internal configuration options
- `_api_connect_options`: Connection settings

### LiveInterpreterSession

**Purpose**: Manages an active translation session

**Key Methods**:
- `__anext__()`: Async iterator for translation results
- `aclose()`: Cleanup and close session
- `push_audio()`: Send audio for translation
- `_start_recognition()`: Initialize Azure SDK
- `_stop_recognition()`: Stop translation

**Event Handlers**:
- `_on_session_started()`: Session initialization
- `_on_recognizing()`: Intermediate results (limited)
- `_on_recognized()`: Final translation results
- `_on_synthesizing()`: Audio synthesis
- `_on_canceled()`: Error handling
- `_on_session_stopped()`: Session cleanup

**Key Attributes**:
- `_recognizer`: Azure TranslationRecognizer instance
- `_audio_stream`: Push audio input stream
- `_event_queue`: Queue for translation results
- `_audio_buffer`: Synthesized audio storage

## Data Flow

### Audio Input Flow

```
LiveKit Audio Frame
    │
    ├─ Sample rate check
    │  └─ Resample if needed (to 16kHz or 24kHz)
    │
    ├─ Convert to bytes
    │
    └─ Push to Azure SDK
       └─ PushAudioInputStream.write()
```

### Translation Output Flow

```
Azure Recognition Event
    │
    ├─ Extract source language
    ├─ Extract source text
    ├─ Extract translations (dict)
    │
    └─ Create ChatChunk
       └─ Queue to _event_queue
          └─ Consumed by async iterator
             └─ Returned to LiveKit Agent
```

### Audio Synthesis Flow

```
Azure Synthesizing Event
    │
    ├─ Extract audio bytes (WAV)
    │
    └─ Buffer storage
       └─ _audio_buffer.extend()
          └─ Available via get_audio_buffer()
             └─ Can be published to LiveKit room
```

## Integration Points

### LiveKit Agents Framework

- Implements `llm.LLM` interface for compatibility
- Implements `llm.LLMStream` for streaming results
- Uses `rtc.AudioFrame` for audio input
- Integrates with `AgentSession` for room management

### Azure Speech SDK

- Uses `SpeechTranslationConfig` with V2 endpoint
- Uses `AutoDetectSourceLanguageConfig` for language detection
- Uses `TranslationRecognizer` for speech processing
- Uses `PushAudioInputStream` for audio input

## Configuration Flow

```
Environment Variables
  ├─ AZURE_SPEECH_KEY
  ├─ AZURE_SPEECH_REGION
  └─ AZURE_SPEAKER_PROFILE_ID (optional)
         │
         ▼
LiveInterpreterModel.__init__()
         │
         ├─ Validate credentials
         ├─ Validate target languages
         └─ Create _LiveInterpreterOptions
                  │
                  ▼
         LiveInterpreterSession
                  │
                  ├─ Build V2 endpoint URL
                  ├─ Configure SpeechTranslationConfig
                  ├─ Set target languages
                  ├─ Configure personal voice
                  └─ Create TranslationRecognizer
```

## Error Handling

### Error Categories

1. **Configuration Errors** (raise immediately)
   - Missing credentials
   - Invalid target languages
   - Invalid region

2. **Connection Errors** (APIConnectionError)
   - Network failures
   - WebSocket connection issues
   - Azure service unavailable

3. **Runtime Errors** (queued to _event_queue)
   - Recognition cancellation
   - Translation errors
   - Synthesis failures

### Error Flow

```
Error Occurrence
    │
    ├─ Logged via logger.error()
    │
    └─ Error Type?
        │
        ├─ Configuration Error
        │  └─ Raise ValueError immediately
        │
        ├─ Connection Error
        │  └─ Raise APIConnectionError
        │
        └─ Runtime Error
           └─ Create APIStatusError
              └─ Queue to _event_queue
                 └─ Re-raised when consumed
```

## Performance Considerations

### Latency

- **Language Detection**: < 5 seconds (first utterance)
- **Translation**: 200-500ms typical
- **Audio Synthesis**: Real-time streaming
- **End-to-End**: ~1-2 seconds total

### Bandwidth

- **Audio Input**: 256-384 Kbps (depending on sample rate)
- **Audio Output**: Similar to input
- **Metadata**: Minimal (JSON events)

### Scalability

- **Per Session**: One WebSocket connection
- **Multi-Session**: Independent connections per agent
- **Azure Limits**: Check service quotas

## Testing Strategy

### Unit Tests

- Data models validation
- Utility functions
- Configuration handling
- Error conditions

### Integration Tests

- Azure SDK interaction (requires credentials)
- Audio streaming
- Translation accuracy
- Error recovery

### Manual Tests

- LiveKit room integration
- Multi-participant scenarios
- Language switching
- Audio quality

## Future Enhancements

1. **Enhanced Error Recovery**
   - Automatic reconnection with exponential backoff
   - Session state recovery
   - Graceful degradation

2. **Performance Optimization**
   - Audio buffer optimization
   - Lazy initialization
   - Connection pooling

3. **Feature Additions**
   - Batch translation support
   - Custom voice training integration
   - Advanced metrics collection
   - Webhook support for events

4. **Security**
   - Azure Managed Identity support
   - Key rotation
   - Audit logging

## References

- [Azure Live Interpreter API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-translate-speech)
- [LiveKit Agents Framework](https://docs.livekit.io/agents/)
- [Azure Speech SDK Python](https://learn.microsoft.com/en-us/python/api/overview/azure/cognitiveservices-speech-readme)
