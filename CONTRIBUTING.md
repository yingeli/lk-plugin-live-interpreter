# Contributing to LiveKit Azure Live Interpreter Plugin

Thank you for your interest in contributing to the LiveKit Azure Live Interpreter Plugin!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Azure Speech Service subscription (for testing)

### Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/lk-plugin-realtime.git
cd lk-plugin-realtime
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
cd livekit-plugins/livekit-plugins-azure
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp examples/.env.example examples/.env
# Edit examples/.env with your Azure credentials
```

## Code Style

We use the following tools for code quality:

- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking

Run before committing:

```bash
# Format code
black livekit/
isort livekit/

# Type check
mypy livekit/
```

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

Integration tests require Azure credentials:

```bash
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="eastus"
pytest tests/integration/
```

### Manual Testing

Test with a LiveKit room:

```bash
cd examples
python simple_interpreter.py dev
```

## Pull Request Process

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes with clear commit messages:
```bash
git commit -m "Add feature: description"
```

3. Ensure tests pass and code is formatted:
```bash
pytest tests/
black livekit/
isort livekit/
mypy livekit/
```

4. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

5. PR checklist:
   - [ ] Tests pass
   - [ ] Code is formatted
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] No breaking changes (or documented)

## Reporting Bugs

Report bugs at: https://github.com/livekit/agents/issues

Include:
- Plugin version
- Python version
- Azure region
- Minimal reproduction code
- Error messages and logs

## Feature Requests

We welcome feature requests! Please:
1. Check existing issues first
2. Describe the use case
3. Explain why it's valuable
4. Propose an implementation if possible

## Code of Conduct

Be respectful and professional. We aim to provide a welcoming environment for all contributors.

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
