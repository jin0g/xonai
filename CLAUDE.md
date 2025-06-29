# xonai - AI Assistant Instructions

This document contains instructions and context for AI assistants working on the xonai project.

## Project Overview

xonai is a tool that integrates AI assistants into xonsh shell by intercepting command-not-found errors and routing them to AI for natural language interpretation.

### Core Architecture

- **Entry Point**: `xonai/xonai.py` launches xonsh with xontrib loaded
- **Xontrib**: `xonai/xontrib.py` overrides `SubprocSpec._run_binary` for command interception
- **AI System**: Modular design in `xonai/ai/` with BaseAI interface
- **Display**: `xonai/display.py` handles formatted terminal output

## Critical Implementation Details for AI Development

### Command Interception Strategy

**IMPORTANT**: The core functionality uses `SubprocSpec._run_binary` override approach:

1. Catches `XonshError` with "command not found" message
2. Routes unrecognized commands to AI instead of showing error
3. Returns dummy successful process to suppress error display
4. Preserves normal xonsh command execution

**DO NOT attempt natural language detection** - it's impossible to reliably distinguish between:
- Natural language queries
- Valid commands/syntax
- User-defined variables

### Signal Handling Requirements

- Use shell script launcher with `exec xonsh` for proper Ctrl-C handling
- Avoid Python subprocess interference with signal propagation
- Use `os.system()` over `subprocess.run()` for better terminal state preservation

### Subprocess Deadlock Prevention

**CRITICAL**: Complex queries can cause deadlock due to stderr buffer blocking.
**Solution**: Use background thread for stderr reading (already implemented in `handler.py`)

## Development Principles for AI

1. **Simplicity First**: Keep implementation as simple as possible
2. **Non-intrusive**: Never interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds
5. **Modularity**: Support multiple AI providers through abstract interfaces

## Current Limitations (Do Not Try to "Fix")

1. No session continuity between queries (Claude CLI architectural limitation)
2. No context awareness (history, environment, cwd not passed to Claude)
3. Output cannot be captured with subshell syntax `$()`
4. No pipeline support for natural language queries
5. Python import usage not supported (xonsh-only design)

**These are intentional design decisions - do not attempt workarounds.**

## Development Commands for AI

### Essential Commands
```bash
# Full development cycle
make all

# Test basic functionality
make test

# Test with actual Claude CLI (requires Claude login)
make test-cc

# Linting and formatting
make lint
make format
```

### Testing Requirements

See `tests/README.md` for comprehensive testing documentation. Key requirements:
- Unit tests must pass before any code changes
- Test both English and Japanese natural language queries
- Verify Ctrl-C handling and subprocess deadlock prevention

## Prohibited Actions for AI

- **NEVER** attempt natural language detection patterns
- **NEVER** modify xonsh event system beyond current approach  
- **NEVER** create complex workarounds for stated limitations
- **NEVER** interfere with normal shell command execution
- **NEVER** commit secrets or API keys
- **NEVER** create GitHub workflows without explicit instruction

## File Structure for AI Reference

```
xonai/
├── xonai/
│   ├── __init__.py         # Package initialization
│   ├── xonai.py           # Entry point (launches xonsh)
│   ├── xontrib.py         # Xonsh integration (command interception)
│   ├── handler.py         # Command handling and AI routing
│   ├── display.py         # Terminal output formatting
│   └── ai/
│       ├── __init__.py    # AI provider registry
│       ├── base.py        # BaseAI abstract interface
│       ├── claude.py      # Claude CLI implementation
│       └── dummy.py       # Testing implementation
├── tests/                 # See tests/README.md for details
├── bin/xonai              # Shell script launcher
├── pyproject.toml         # Package configuration
├── README.md              # User documentation
├── DEVELOPMENT.md         # Developer documentation
└── CLAUDE.md              # This file (AI instructions)
```

## AI Response Protocol

xonai uses structured Response objects for AI communication:

### Response Types
1. **InitResponse**: Session start (`content`: AI name, `session_id`, `model`)
2. **MessageResponse**: AI text messages (supports streaming)
3. **ToolUseResponse**: Tool usage notification (`tool`, `content`)
4. **ToolResultResponse**: Tool execution result
5. **ErrorResponse**: Error notification (hidden from users)
6. **ResultResponse**: Session end with statistics

### Display Rules for AI
- **InitResponse**: Show after blank line with emoji
- **MessageResponse**: Stream continuously
- **ToolUseResponse**: Show concisely with emoji (🔧📖✏️📁🔍📋📝🌐)
- **ToolResultResponse**: Show indented summary
- **ErrorResponse**: Hide from user
- **ResultResponse**: Show statistics after blank line

## Deployment Information for AI

### PyPI Publishing Process
1. Update version in `pyproject.toml`
2. Create version tag: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions automatically publishes to PyPI

**DO NOT** manually publish unless explicitly instructed.

## Adding New AI Providers (for AI Development)

### Implementation Steps
1. Create new class inheriting from `BaseAI` in `xonai/ai/`
2. Implement required methods: `process()`, `is_available()`
3. Add to `AI_PROVIDERS` mapping in `xonai/ai/__init__.py` 
4. Add comprehensive tests (see tests/README.md for guidelines)
5. Update documentation in DEVELOPMENT.md

### BaseAI Interface Requirements
```python
class BaseAI(ABC):
    @abstractmethod
    def process(self, query: str) -> Generator[Response, None, None]:
        """Process query and yield Response objects"""
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if AI provider is available"""
```

## Important Context for AI

### Project Status
xonai v0.1.0 is production-ready. All critical issues resolved:
- Subprocess deadlock fix (background thread for stderr)
- PyPI Trusted Publisher deployment
- Comprehensive test coverage
- Complete documentation restructure

### Current Branch: `prepare-for-release`
Main development branch is `main`. Use `main` for PRs unless specifically instructed otherwise.

### When Making Changes
1. Always run `make all` after changes
2. Test thoroughly with both English and Japanese queries
3. Verify Ctrl-C handling works correctly
4. Run appropriate tests per tests/README.md guidelines
5. Update relevant documentation (README.md for users, DEVELOPMENT.md for developers)
6. Keep this CLAUDE.md updated with any AI-specific instructions

### Documentation Roles
- **README.md**: User-facing installation and usage guide
- **DEVELOPMENT.md**: Developer setup, testing, deployment, architecture
- **CLAUDE.md**: AI assistant instructions and project context (this file)

**Never duplicate content between these files.**

---

**This document should be updated whenever AI development context changes.**