# xonai Development Guide

This document provides technical information for developers who want to contribute to xonai.

## Architecture Overview

xonai integrates AI assistants into xonsh shell by catching command-not-found errors and passing them to AI for interpretation.

### Key Components

1. **xonai command** (`xonai/xonai`)
   - Shell script that launches xonsh with xonai xontrib loaded
   - Loads user's existing .xonshrc and adds xontrib automatically

2. **xontrib** (`xonai/xontrib.py`)
   - Overrides `SubprocSpec._run_binary` to intercept command execution
   - Uses modular AI system with BaseAI interface
   - Uses `claude --print --output-format stream-json` for real-time output

3. **AI System** (`xonai/agents/`)
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
│   ├── xonai             # Shell script launcher
│   ├── xontrib.py        # Xonsh integration
│   ├── handler.py        # Command handling and AI routing
│   ├── display.py        # Output formatting
│   └── agents/
│       ├── __init__.py
│       ├── base.py       # Abstract AI interface
│       ├── claude.py     # Claude implementation
│       └── dummy.py      # Test implementation
├── tests/                # See tests/README.md
├── pyproject.toml
├── README.md
└── DEVELOPMENT.md
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

## AI Assistant Instructions

This section contains specific instructions for AI assistants working on the xonai project.

### Project Overview

xonai integrates AI assistants into xonsh shell by intercepting command-not-found errors and routing them to AI for natural language interpretation.

### Core Architecture

- **Entry Point**: `xonai/xonai.py` launches xonsh with xontrib loaded
- **Xontrib**: `xonai/xontrib.py` overrides `SubprocSpec._run_binary` for command interception
- **AI System**: Modular design in `xonai/agents/` with BaseAI interface
- **Display**: `xonai/display.py` handles formatted terminal output

### Critical Implementation Details for AI Development

#### Command Interception Strategy

**IMPORTANT**: The core functionality uses `SubprocSpec._run_binary` override approach:

1. Catches `XonshError` with "command not found" message
2. Routes unrecognized commands to AI instead of showing error
3. Returns dummy successful process to suppress error display
4. Preserves normal xonsh command execution

**DO NOT attempt natural language detection** - it's impossible to reliably distinguish between:
- Natural language queries
- Valid commands/syntax
- User-defined variables

#### Signal Handling Requirements

- Use shell script launcher with `exec xonsh` for proper Ctrl-C handling
- Avoid Python subprocess interference with signal propagation
- Use `os.system()` over `subprocess.run()` for better terminal state preservation

#### Subprocess Deadlock Prevention

**CRITICAL**: Complex queries can cause deadlock due to stderr buffer blocking.
**Solution**: Use background thread for stderr reading (already implemented in `handler.py`)

### Development Principles for AI

1. **Simplicity First**: Keep implementation as simple as possible
2. **Non-intrusive**: Never interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds
5. **Modularity**: Support multiple AI providers through abstract interfaces

### Current Limitations (Do Not Try to "Fix")

1. No session continuity between queries (Claude CLI architectural limitation)
2. No context awareness (history, environment, cwd not passed to Claude)
3. Output cannot be captured with subshell syntax `$()`
4. No pipeline support for natural language queries
5. Python import usage not supported (xonsh-only design)

**These are intentional design decisions - do not attempt workarounds.**

### Development Commands for AI

See `tests/README.md` for comprehensive command reference and testing documentation.

### Prohibited Actions for AI

- **NEVER** attempt natural language detection patterns
- **NEVER** modify xonsh event system beyond current approach  
- **NEVER** create complex workarounds for stated limitations
- **NEVER** interfere with normal shell command execution
- **NEVER** commit secrets or API keys
- **NEVER** create GitHub workflows without explicit instruction

### File Structure for AI Reference

```
xonai/
├── xonai/
│   ├── __init__.py         # Package initialization
│   ├── xonai               # Shell script launcher
│   ├── xontrib.py         # Xonsh integration (command interception)
│   ├── handler.py         # Command handling and AI routing
│   ├── display.py         # Terminal output formatting
│   └── agents/
│       ├── __init__.py    # AI provider registry
│       ├── base.py        # BaseAI abstract interface
│       ├── claude.py      # Claude CLI implementation
│       └── dummy.py       # Testing implementation
├── tests/                 # See tests/README.md for details
├── pyproject.toml         # Package configuration
├── README.md              # User documentation
└── DEVELOPMENT.md         # This file (developer and AI instructions)
```

### AI Response Protocol

xonai uses structured Response objects for AI communication:

#### Response Types
1. **InitResponse**: Session start (`content`: AI name, `session_id`, `model`)
2. **MessageResponse**: AI text messages (supports streaming)
3. **ToolUseResponse**: Tool usage notification (`tool`, `content`)
4. **ToolResultResponse**: Tool execution result
5. **ErrorResponse**: Error notification (hidden from users)
6. **ResultResponse**: Session end with statistics

#### Display Rules for AI
- **InitResponse**: Show after blank line with emoji
- **MessageResponse**: Stream continuously
- **ToolUseResponse**: Show concisely with emoji (🔧📖✏️📁🔍📋📝🌐)
- **ToolResultResponse**: Show indented summary
- **ErrorResponse**: Hide from user
- **ResultResponse**: Show statistics after blank line

### Deployment Information for AI

#### PyPI Publishing Process
1. Update version in `pyproject.toml`
2. Create version tag: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions automatically publishes to PyPI

**DO NOT** manually publish unless explicitly instructed.

### Adding New AI Providers (for AI Development)

#### Implementation Steps
1. Create new class inheriting from `BaseAI` in `xonai/agents/`
2. Implement required methods: `process()`, `is_available()`
3. Add to `AI_PROVIDERS` mapping in `xonai/agents/__init__.py` 
4. Add comprehensive tests (see tests/README.md for guidelines)
5. Update documentation in DEVELOPMENT.md

#### BaseAI Interface Requirements
```python
class BaseAI(ABC):
    @abstractmethod
    def process(self, query: str) -> Generator[Response, None, None]:
        """Process query and yield Response objects"""
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if AI provider is available"""
```

### Important Context for AI

#### Project Status
xonai v0.1.0 is production-ready. All critical issues resolved:
- Subprocess deadlock fix (background thread for stderr)
- PyPI Trusted Publisher deployment
- Comprehensive test coverage
- Complete documentation restructure

Main development branch is `main`. Use `main` for PRs unless specifically instructed otherwise.

#### When Making Changes
1. Follow development workflow in `tests/README.md`
2. Test thoroughly with both English and Japanese queries
3. Verify Ctrl-C handling works correctly
4. Update relevant documentation (README.md for users, DEVELOPMENT.md for developers)

#### Documentation Roles
- **README.md**: User-facing installation and usage guide
- **DEVELOPMENT.md**: Developer setup, testing, deployment, architecture, and AI instructions (this file)
- **tests/README.md**: Comprehensive testing documentation

**Never duplicate content between these files.**