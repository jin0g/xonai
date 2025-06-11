# xoncc Development Notes

This document contains important development notes, implementation details, and usage documentation for xoncc.

## Overview

xoncc is a simple xonsh extension that catches "command not found" errors and automatically asks Claude AI for help. No special commands needed - just type naturally in any language.

## Usage Guide

### Installation Methods

1. **Launch with xoncc command (Recommended)**
   ```bash
   xoncc
   ```

2. **Load as xontrib in existing xonsh session**
   ```bash
   xonsh
   >>> xontrib load xoncc
   ```

3. **Auto-load in .xonshrc**
   Add to your `~/.xonshrc`:
   ```python
   xontrib load xoncc
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
- **Session continuity**: Conversations are maintained within a session
- **Transparent operation**: No special syntax or commands to remember
- **Safe**: Only activates for non-existent commands

## Important Notes

- **xonsh shell only**: This package is designed specifically as a xonsh extension. Python import usage is not supported.
- **Claude Code required**: You need Claude Code installed and accessible in your PATH.
- **Auto-login**: Login to Claude will be handled automatically when needed.

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

# Install xoncc in development mode
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

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests (includes interactive tests if expect is available)
make test

# Run lint
make lint

# Install locally
make install

# Clean build artifacts
make clean
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests
- `tests/interactive/` - Interactive shell tests (requires expect)
- `tests/dummy_claude/` - Tests using mock Claude CLI

### Dummy Claude Environment

For testing without real Claude CLI, set the environment variable:
```bash
export XONCC_DUMMY=1
```

This will use `dummy_claude` command instead of `claude`.

## Architecture Overview

xoncc integrates Claude AI into xonsh shell by catching command-not-found errors and passing them to Claude for interpretation.

### Key Components

1. **xoncc shell script** (`xoncc/xoncc`)
   - Simple bash script that launches xonsh with xoncc xontrib loaded
   - Uses `exec xonsh` to properly handle signals (especially Ctrl-C)

2. **xontrib** (`xoncc/xontrib.py`)
   - Overrides `SubprocSpec._run_binary` to intercept command execution
   - Calls Claude CLI directly with auto-login handling
   - Uses `claude --print --output-format stream-json` for real-time output

3. **Claude CLI integration** (`call_claude_direct` function)
   - Direct subprocess-based Claude CLI invocation
   - Auto-detects login errors and triggers login process
   - Retries original command after successful login

4. **Real-time JSON formatter** (`xoncc/formatters/`)
   - Modular formatter package for Claude's streaming JSON output
   - Displays token count and tool usage during processing
   - Handles both streaming and log output formats

## Implementation Challenges & Solutions

### 1. Ctrl-C Handling
**Problem**: Initial Python-based xoncc wrapper caused shell to exit on Ctrl-C.

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

**Solution**: Using `os.system()` instead of `subprocess.run()` for better real-time display.

### 4. Natural Language Detection
**Important Decision**: Avoid pattern matching approaches. It's impossible to perfectly distinguish between:
- Natural language queries
- Valid commands/syntax
- User-defined variables

Attempting partial detection causes more harm than good.

### 5. Auto-Login Implementation
**Solution**: Use Claude CLI's behavior to detect login status:
- `claude --print --output-format stream-json "query"` fails with "Invalid API key" when not logged in
- Detect this error in JSON output stream
- Automatically run `claude /exit` to trigger login process
- Retry original command after login completes

**Benefits**:
- No complex login status checking required
- Works with Claude CLI's natural authentication flow
- Seamless user experience

## Design Principles

1. **Simplicity**: Keep the implementation as simple as possible
2. **Non-intrusive**: Don't interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds

## Known Limitations

1. ~~Natural language queries display as command-not-found errors~~ (Fixed!)
2. ~~Login status checking required at startup~~ (Fixed with auto-login!)
3. No context awareness (history, environment, cwd not passed to Claude)
4. Output cannot be captured with subshell syntax `$()`
5. No pipeline support for natural language queries
6. Python import usage not supported (xonsh-only design)

## Development Roadmap

### ✅ Completed Features
- [x] AI processing recognized as normal command (not error)
- [x] Real-time display of AI processing progress with token counts
- [x] Clean output formatting for both streaming and log modes
- [x] Code organized into functional modules with comprehensive tests
- [x] Auto-login handling for Claude CLI
- [x] Shell script-based xoncc launcher

### 🚧 In Progress  
- [ ] Ctrl-C handling improvement
  - Basic handling works but may occasionally cause issues
  - Testing cleaner subprocess management approaches

### 📋 Future Improvements

#### Output Capture Support
- [ ] Enable output capture from Claude responses
  - **Goal**: Support `$(claude_query)` syntax to capture AI responses in variables
  - **Implementation**: Modify Claude CLI call to return output instead of printing
  - **Challenges**: Need to distinguish between interactive and capture modes
  - **Example**: `files=$(how do I list large files)` should work

#### Pipeline Support
- [ ] Add pipeline support for natural language queries
  - **Goal**: Allow piping AI responses to other commands
  - **Implementation**: Make Claude output pipeable by treating it as command output
  - **Example**: `how to list files | grep python` should pipe AI response to grep
  - **Challenges**: Distinguishing when user wants to pipe vs when they're asking about pipes

#### Shell Context Awareness
- [ ] Pass shell context (history, env, cwd) to AI
  - **Goal**: Make Claude aware of current shell state for better responses
  - **Implementation**: Pass current directory, recent commands, and environment to Claude
  - **Context to include**:
    - Current working directory
    - Recent command history (last 10 commands)
    - Key environment variables (PATH, etc.)
    - Git repository status if applicable
  - **Privacy considerations**: Allow users to opt-out of context sharing

#### Parallel Processing & Advanced Control
- [ ] AI processing and shell execution in parallel
  - **Goal**: Run AI and shell commands simultaneously without blocking
  - **Implementation**: Background AI processing with foreground shell availability
  - **User Interface**:
    - Ctrl+C once: Interrupt AI with y/n confirmation prompt
    - Ctrl+C twice: Force quit everything
    - Status indicators for background AI processing
  
- [ ] Add queue for AI instructions
  - **Goal**: Queue multiple AI requests or enable parallel AI executions
  - **Implementation**: Background job management system
  - **Features**:
    - Queue multiple queries: `cc-queue "query1" "query2" "query3"`
    - Status checking: `cc-status` to see running/queued jobs
    - Result retrieval: `cc-result <job-id>` to get specific results

#### UI/UX Improvements
- [ ] Fix status line display during AI processing
  - **Goal**: Clean, non-intrusive progress indicators
  - **Implementation**: Single-line status updates without interfering with output
  - **Features**:
    - Token count display
    - Processing time
    - Cost estimation
    - Progress bar for long operations

#### Compatibility & Edge Cases
- [ ] Handle fullscreen mode during parallel execution
  - **Goal**: Graceful handling of fullscreen applications during AI processing
  - **Challenges**: How to display AI results when vim/emacs is running
  - **Solutions to explore**:
    - Notification system
    - Background completion with retrieval commands
    - Terminal multiplexer integration

## Development Tips

1. Always run `make all` after making changes
2. Test Ctrl-C handling thoroughly
3. Test with both English and Japanese queries
4. Avoid complex pattern matching logic
5. Keep xonsh's event system behavior in mind

## Testing Strategy

### Test Categories

1. **Unit Tests** (`make test`)
   - No external dependencies
   - Mock Claude CLI interactions
   - Run in CI/CD environment
   - Fast execution

2. **Integration Tests** (`make test-cc`)
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
python -m pytest tests/test_setup_claude.py tests/test_formatters_*.py tests/test_xoncc_simple.py -v
```

### Local Testing with Claude CLI

```bash
# Test basic functionality
make test

# Test with actual Claude CLI (requires login)
make test-cc

# Run specific Claude CLI tests
python -m pytest tests/test_claude_cli_integration.py -v

# Run tests with specific markers
python -m pytest -m "claude_cli" -v
python -m pytest -m "not claude_cli" -v
```

## Technical Details

### xonsh Event System
- `on_command_not_found` only fires in interactive mode
- Events cannot prevent subsequent error handling
- Event handlers should be lightweight

### Clean xontrib Implementation (Current)
- Use only official xonsh event system (`on_command_not_found`)
- Direct Claude CLI subprocess integration
- Smart command filtering to skip common typos
- Auto-login handling with error detection and retry
- Functions added to xonsh context: `cc()` and `claude()`

### Signal Handling
- Shell scripts with `exec` provide cleanest signal handling
- Python subprocess module can interfere with signal propagation
- `os.system()` preserves terminal state better than `subprocess.run()`