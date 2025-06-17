# xonai Development Notes

This document contains important development notes, implementation details, and usage documentation for xonai (formerly xoncc).

## Overview

xonai is a modular xonsh extension that catches "command not found" errors and automatically asks AI for help. No special commands needed - just type naturally in any language. The architecture supports multiple AI models, starting with Claude.

## Usage Guide

### Installation Methods

1. **Launch with xonai command (Recommended)**
   ```bash
   xonai
   ```

2. **Load as xontrib in existing xonsh session**
   ```bash
   xonsh
   >>> xontrib load xonai
   ```

3. **Auto-load in .xonshrc**
   Add to your `~/.xonshrc`:
   ```python
   xontrib load xonai
   ```

### Examples

```bash
# Ask questions naturally in English
>>> how do I find large files
To find large files, you can use the `find` command...

# Japanese queries work too
>>> 大きなファイルを探す方法
大きなファイルを探すには、`find`コマンドを使用します...

# Regular commands work normally
>>> ls
>>> print("Hello World")
```

## Features

- **Zero configuration**: Works immediately after installation
- **Multi-language support**: Ask questions in English, Japanese, or any language
- **Modular AI support**: Extensible architecture for multiple AI models
- **Transparent operation**: No special syntax or commands to remember
- **Safe**: Only activates for non-existent commands

## Important Notes

- **xonsh shell only**: This package is designed specifically as a xonsh extension. Python import usage is not supported.
- **Claude Code required**: For Claude AI support, you need Claude Code installed and accessible in your PATH.
- **Claude login required**: You need to be logged in to Claude CLI before using Claude AI.

## Development & Testing

### Setting Up Development Environment

**IMPORTANT**: Always use a virtual environment for development:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Install xonai in development mode
pip install -e .
```

### Git Best Practices

**CRITICAL**: Never commit the virtual environment or use `git add .` / `git add -A`:

```bash
# ✅ GOOD: Add specific files
git add file1.py file2.py

# ✅ GOOD: Add only tracked files
git add -u

# ❌ BAD: Never use these
git add .
git add -A
```

The `venv/` directory is included in `.gitignore` and must NEVER be committed to the repository.

### Development Commands

```bash
# Activate virtual environment first
source venv/bin/activate

# Install xonai in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Run all tests with coverage and linting
python -m pytest
# or simply
pytest

# Run tests for specific modules
pytest tests/unit/
pytest tests/integration/
pytest -m "not claude_cli"  # Skip tests requiring Claude CLI

# Run linting only
ruff check xonai/ tests/
ruff format --check xonai/ tests/
mypy xonai/ --ignore-missing-imports

# Auto-format code
ruff check xonai/ tests/ --fix
ruff format xonai/ tests/

# Install for current user (not in venv)
pip install --user .

# Uninstall
pip uninstall xonai

# Clean build artifacts
rm -rf build/ dist/ *.egg-info/
rm -rf .pytest_cache/ htmlcov/
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Quick Start for Contributors

```bash
# Clone and setup
git clone https://github.com/jin0g/xonai
cd xonai
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests before making changes
pytest

# Make your changes, then test again
pytest

# Format your code
ruff format xonai/ tests/

# Check everything before committing
pytest  # This runs tests + linting via pytest-ruff
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests
- `tests/interactive/` - Interactive shell tests (requires expect)
- `tests/dummy_claude/` - Tests using mock Claude CLI

### Dummy Claude Environment

For testing without real Claude CLI, set the environment variable:
```bash
export XONAI_DUMMY=1
```

This will use `dummy_claude` command instead of `claude`.

## Architecture Overview

xonai integrates AI assistants into xonsh shell by catching command-not-found errors and passing them to AI for interpretation.

### Key Components

1. **xonai shell script** (`xonai/xonai`)
   - Simple bash script that launches xonsh with xonai xontrib loaded
   - Uses `exec xonsh` to properly handle signals (especially Ctrl-C)

2. **xontrib** (`xonai/xontrib.py`)
   - Overrides `SubprocSpec._run_binary` to intercept command execution
   - Calls Claude CLI directly with auto-login handling
   - Uses `claude --print --output-format stream-json` for real-time output

3. **AI System** (`xonai/ai/`)
   - Modular AI architecture with base classes
   - `Response` class hierarchy for structured responses
   - `ClaudeAI` implementation using Claude CLI
   - `DummyAI` for testing

4. **Real-time JSON formatter** (`xonai/display.py`)
   - Formats Claude's streaming JSON output with emoji-based display
   - Uses Rich library for proper text width measurement and styling
   - Handles wide characters (Japanese, emoji) correctly
   - Displays token count and tool usage during processing
   - Smart truncation that respects terminal width

## Implementation Challenges & Solutions

### 1. Ctrl-C Handling
**Problem**: Initial Python-based xonai wrapper caused shell to exit on Ctrl-C.

**Solution**: Switched to shell script with `exec xonsh`, allowing xonsh to handle signals naturally.

### 2. Error Status Display
**Problem**: Natural language queries show as command-not-found errors.

**Attempted Solutions**:
- `on_transform_command` - Caused issues with normal command execution
- Pattern matching for natural language detection - Imperfect and harmful (rejected by user)
- Function override of `SubprocSpec._run_binary` - Successfully implemented!

**Solution**: Override `SubprocSpec._run_binary` to catch `XonshError` with "command not found" message and return a dummy successful process instead of raising the error. This completely eliminates error messages for natural language queries while preserving normal functionality.

### 3. Real-time Output
**Problem**: Initial implementation buffered output.

**Solution**: Using `subprocess.Popen` with unbuffered output for real-time streaming display.

### 4. Natural Language Detection
**Important Decision**: Avoid pattern matching approaches. It's impossible to perfectly distinguish between:
- Natural language queries
- Valid commands/syntax
- User-defined variables

Attempting partial detection causes more harm than good.


### 6. Session Continuity Implementation  
**Solution**: Use Claude's native session continuation with global variable storage:
- Session ID stored from INIT message in global variable `session_id` in `cc.py`
- Before `--continue` commands, update timestamp in `~/.claude/projects/{path}/{session_id}.jsonl` 
- Use `claude --continue` for subsequent queries instead of passing context directly
- Working directory path converted to session path format (/ replaced with -)

**Implementation Details**:
- `update_session_timestamp()` function in `cc.py` handles timestamp updates
- Session file path: `~/.claude/projects/-path-to-directory/{session_id}.jsonl`
- Updates timestamp of last JSON line to current time before `--continue`
- Global variable `session_id` maintains state within the xonsh process
- Gracefully handles missing files or JSON parsing errors

**Current Status (CONFIRMED NOT WORKING)**: 
- ❌ Session continuity is **NOT functioning** with real Claude CLI
- `--continue` flag is implemented correctly in xonai code (but removed in refactoring)
- Session IDs change with each `--continue` invocation (expected behavior)
- Claude CLI does not maintain conversation memory across `--continue` calls
- **Definitive Test**: Passphrase memory test with "柘榴の花" (pomegranate flower) **FAILED**
  - First query: "合言葉は「柘榴の花」です。覚えておいて下さい。メモは取らないでください。"
  - Second query with `--continue`: "合言葉を覚えていますか？"
  - Result: Claude responded "新しいセッションのようです" (appears to be a new session)
- Timestamp updates (JSON and file mtime) work correctly but do not resolve the issue
- **Root Cause**: Claude CLI's `--continue` flag creates new sessions rather than continuing existing ones

**Testing Strategy**:
- **Real Claude CLI**: Use actual `claude` command for integration testing (but session continuity fails)
- **Dummy Claude CLI**: Use mock implementation for CI/Actions testing (simulates working session continuity)
- Environment variable `XONAI_DUMMY=1` switches between real and dummy modes
- Local development requires both real and dummy tests to pass 100%
- Actions only runs dummy tests to avoid Claude CLI dependency
- **Important**: Dummy tests pass to verify implementation correctness, but real Claude CLI has limitations

## Design Principles

1. **Simplicity**: Keep the implementation as simple as possible
2. **Non-intrusive**: Don't interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds

## Technical Limitations

1. **Session continuity not functional**: Claude CLI's `--continue` flag does not maintain conversation memory
2. **Process-scoped implementation**: Session logic is implemented within single xonsh process only  
3. **No output capture**: Cannot use `$(natural language query)` syntax yet  
4. **No pipeline support**: Cannot pipe natural language output to other commands
5. **xonsh-only design**: Not usable as regular Python import

## Current Implementation Status

### ✅ Completed Features
- [x] Natural language command interpretation via `SubprocSpec._run_binary` override
- [x] Emoji-rich output formatting with tool indicators  
- [x] Real-time Claude CLI streaming with progress display
- [x] Session continuity implementation (code complete, but Claude CLI limitation prevents functionality)
- [x] Shell script launcher with proper signal handling
- [x] Comprehensive test suite with unit/integration/dummy tests

### 📋 Planned Features (matches README.md)
- [ ] Markdown syntax highlighting and colorization
- [ ] Detailed tool results display
- [ ] Output capture with `$()` syntax
- [ ] Pipeline support for natural language queries
- [ ] Parallel AI processing with improved Ctrl+C handling

## Development Tips

1. Always run tests after making changes: `pytest`
2. Test Ctrl-C handling thoroughly
3. Test with both English and Japanese queries
4. Avoid complex pattern matching logic
5. Keep xonsh's event system behavior in mind
6. Use ruff for consistent code formatting: `ruff format xonai/ tests/`

## Testing Strategy

### Test Categories

1. **Unit Tests**
   - No external dependencies
   - Mock Claude CLI interactions
   - Run in CI/CD environment
   - Fast execution
   - Run with: `pytest tests/unit/`

2. **Integration Tests**
   - May require Claude CLI
   - Test actual AI interactions
   - Run with: `pytest tests/integration/`
   - Require Claude CLI installation
   - Test actual AI interactions
   - Local development only
   - May take longer to execute


### Test Markers

- `@pytest.mark.claude_cli`: Tests requiring Claude CLI
- `@pytest.mark.integration`: Integration tests (may be slow)
- `@pytest.mark.slow`: Slow-running tests

### CI/CD Testing

GitHub Actions runs only unit tests without Claude CLI:
```bash
python -m pytest -m "not claude_cli" -v
```

### Local Testing with Claude CLI

```bash
# Test all functionality (including linting)
pytest

# Test without Claude CLI
pytest -m "not claude_cli"

# Test with actual Claude CLI (requires login)
pytest -m "claude_cli"

# Run specific test files
pytest tests/unit/test_formatters_log.py -v
pytest tests/integration/ -v

# Run with coverage report
pytest --cov=xonai --cov-report=html
# Then open htmlcov/index.html in browser
```

## Technical Details

### xonsh Event System
- `on_command_not_found` only fires in interactive mode
- Events cannot prevent subsequent error handling
- Event handlers should be lightweight

### Clean xontrib Implementation (Current)
- Override `SubprocSpec._run_binary` to intercept command execution
- Falls back to `on_command_not_found` event system if needed
- Direct Claude CLI subprocess integration
- Smart command filtering to skip common typos
- Passes shell context and history to Claude

### Signal Handling
- Shell scripts with `exec` provide cleanest signal handling
- Python subprocess module can interfere with signal propagation
- `os.system()` preserves terminal state better than `subprocess.run()`

## Output Formatting System

The formatter uses emoji indicators and Rich library for clean display:

### Key Features
- **Emoji indicators**: 🚀 INIT, 💬 messages, 🔧 tools, 📊 results, ❌ errors  
- **Smart truncation**: Respects terminal width, handles wide characters
- **Tool result hiding**: Most outputs hidden to reduce clutter
- **Todo styling**: Color-coded task status (🔷 pending, 🔄 progress, ✅ done)
- **Rich integration**: Proper ANSI handling and text measurement

### Implementation Details
- **Session storage**: Removed (session management deprecated) 
- **Dependencies**: Rich library (>=13.0.0) for styling and measurement
- **Command flags**: Uses `--continue` for session continuation (deprecated in xonai)
- **Tool results**: Most hidden except empty outputs and grep summaries

## Refactoring from xoncc to xonai

### Background
The project was renamed from xoncc (xonsh on Claude Code) to xonai to reflect its broader vision of supporting multiple AI models, not just Claude.

### Architecture Changes

1. **Modular AI System**
   - Created `ai/` package with base class `BaseAI`
   - Each AI implementation extends `BaseAI` and yields `Response` objects
   - Supports Claude, Dummy (for testing), and future AI models

2. **Structured Response Format**
   - `Response` base class with inheritance hierarchy
   - Each response type (Init, Message, ToolUse, etc.) extends `Response`
   - `ContentType` enum for content formatting (TEXT, JSON, MARKDOWN)
   - No metadata field - all data as direct class attributes

3. **Separation of Concerns**
   - `ai/` - AI model implementations
   - `display.py` - Formatting and display logic (formerly formatter.py)
   - `xontrib.py` - xonsh integration layer

4. **Session Management Removal**
   - Removed session continuity features (session_id, --continue)
   - Claude CLI's --continue flag doesn't maintain conversation memory
   - Future session management will be handled at xonai level, not AI level

### Design Decisions

1. **Why Response class hierarchy over single class with type field?**
   - Type safety and IDE support
   - Clear contract between AI implementations and display layer
   - Easy to extend with new fields without breaking existing code

2. **Why remove session management?**
   - Claude CLI's session continuity doesn't work as expected
   - Better to implement at the xonai level for all AI models
   - Simplifies individual AI implementations

3. **Why keep the shell script launcher?**
   - Clean signal handling (especially Ctrl-C)
   - Consistent with xonsh ecosystem practices
   - Simple and reliable

4. **Why Generator pattern for AI responses?**
   - Supports streaming output (better UX)
   - Memory efficient for large responses
   - Natural fit for real-time display

### Future Extensibility

The new architecture makes it easy to add new AI models:

```python
class NewAI(BaseAI):
    def __call__(self, prompt: str) -> Generator[Response, None, None]:
        # Implementation here
        yield MessageResponse(content="Response")
    
    @property
    def name(self) -> str:
        return "NewAI"
    
    @property
    def is_available(self) -> bool:
        # Check if the AI is available
        return True
```

Then register in `xontrib.py` or make it configurable via environment variables.