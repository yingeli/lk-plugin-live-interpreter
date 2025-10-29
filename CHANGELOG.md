# Changelog

All notable changes to the LiveKit Azure Live Interpreter Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-28

### Added
- Initial release of LiveKit Azure Live Interpreter Plugin
- Support for Azure Live Interpreter API (Preview)
- `LiveInterpreterModel` class for real-time speech translation
- `LiveInterpreterSession` for managing translation sessions
- Automatic language detection with open-range support
- Personal voice preservation across translations
- Support for 90+ target languages
- Multi-language simultaneous translation
- Configurable audio sample rates (16kHz, 24kHz)
- Word-level timestamp support
- Profanity filtering options
- Integration with LiveKit Agents framework
- Three example implementations:
  - Simple interpreter
  - Multi-language meeting interpreter
  - Custom voice profile interpreter
- Comprehensive documentation and examples
- Utility functions for language validation and audio processing

### Known Limitations
- Limited intermediate results with open-range language detection
- No function calling support (translation-only)
- Preview feature (API may change)
- Language switching at sentence boundaries only

## [Unreleased]

### Planned
- Support for Azure Entra ID authentication
- Enhanced error recovery and reconnection logic
- Metrics and monitoring integration
- Batch translation support
- Additional voice customization options
- Performance optimizations for multi-language scenarios
