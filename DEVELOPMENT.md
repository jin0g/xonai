# xonai Development Guide

This document provides technical information for developers who want to contribute to xonai.

## Architecture Overview

xonai integrates AI assistants into xonsh shell by catching command-not-found errors and passing them to AI for interpretation.

### Key Components

1. **xonai command** (`xonai/xonai.py`)
   - Python entry point that launches xonsh with xonai xontrib loaded
   - Creates temporary xonshrc file for proper xontrib loading

2. **xontrib** (`xonai/xontrib.py`)
   - Overrides `SubprocSpec._run_binary` to intercept command execution
   - Uses modular AI system with BaseAI interface
   - Uses `claude --print --output-format stream-json` for real-time output

3. **AI System** (`xonai/ai/`)
   - Modular architecture with BaseAI abstract class
   - ClaudeAI implementation using Claude CLI
   - DummyAI for testing
   - Response class hierarchy for structured communication

4. **Display System** (`xonai/display.py`)
   - ResponseFormatter class for formatting AI responses
   - Uses Rich library for terminal width handling
   - Emoji-based display with tool indicators
   - Smart truncation for long outputs

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Claude Code CLI (for integration testing)

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jin0g/xonai.git
   cd xonai
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Testing

See `tests/README.md` for comprehensive testing documentation including test categories, execution strategies, and debugging procedures.

### Quick Start

```bash
# Development testing (fast)
python -m pytest tests/unit/ -v

# Full testing (requires Claude CLI)
python -m pytest tests/ -v

# Make targets
make test      # Unit tests only
make test-cc   # Full test suite including Claude CLI
```

## Code Quality

### Linting and Formatting

```bash
# Check code style
python -m ruff check xonai/ tests/

# Format code
python -m ruff format xonai/ tests/

# Type checking
python -m mypy xonai/
```

### Configuration

- **Ruff**: Configured in `pyproject.toml` for linting and formatting
- **MyPy**: Type checking configuration in `pyproject.toml`
- **Pytest**: Test configuration and markers in `pyproject.toml`

## Build and Packaging

### Building the Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*
```

### Package Structure

```
xonai/
├── xonai/
│   ├── __init__.py
│   ├── xonai.py          # Main entry point
│   ├── xontrib.py        # Xonsh integration
│   ├── display.py        # Output formatting
│   └── ai/
│       ├── __init__.py
│       ├── base.py       # Abstract AI interface
│       ├── claude.py     # Claude implementation
│       └── dummy.py      # Test implementation
├── tests/
├── pyproject.toml
└── README.md
```

## Deployment

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **Test Workflow** (`test.yml`): Runs on all PRs and pushes
- **Publish Workflow** (`publish.yml`): Deploys to PyPI on version tags

### PyPI Deployment

1. **Automated Deployment** (Recommended):
   - Uses PyPI Trusted Publisher (OIDC)
   - Triggered by creating version tags: `git tag v0.1.0 && git push origin v0.1.0`
   - No API tokens required

2. **Manual Deployment**:
   ```bash
   twine upload dist/*
   ```

### Release Process

1. Update version in `pyproject.toml`
2. Create and push version tag
3. GitHub Actions automatically runs tests and publishes to PyPI

## Technical Implementation Details

### Command Interception

xonai overrides `SubprocSpec._run_binary` method to catch command-not-found errors:
- Catches `XonshError` with "command not found" message
- Passes query to AI for interpretation instead of raising error
- Returns dummy successful process to suppress error display
- Preserves normal command execution for valid commands

### AI Response Protocol

xonai uses a typed Response object streaming protocol:

1. **InitResponse**: Session start notification
2. **MessageResponse**: Text messages from AI (streaming support)
3. **ToolUseResponse**: Tool usage notification
4. **ToolResultResponse**: Tool execution result
5. **ErrorResponse**: Error notification (hidden from users)
6. **ResultResponse**: Session end with statistics

### Error Handling

- Subprocess deadlock prevention using background threads
- Graceful handling of Ctrl-C interruption
- Proper cleanup of resources and threads
- Smart filtering of common command typos

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all public functions
- Write docstrings for classes and public methods
- Keep functions focused and small

### Commit Messages

Use conventional commit format:
```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add tests
refactor: improve code structure
```

### Pull Request Process

1. Create feature branch from `main`
2. Make changes with appropriate tests
3. Ensure all tests pass and code is properly formatted
4. Create pull request with clear description
5. Address review feedback

## Design Principles

1. **Simplicity**: Keep implementation as simple as possible
2. **Non-intrusive**: Don't interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds
5. **Modularity**: Support multiple AI models through abstract interfaces