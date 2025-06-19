# xonai Development Notes

This document contains important development notes and implementation details for xonai.

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

### 5. Command Interception
**Solution**: Override `SubprocSpec._run_binary` method:
- Catches `XonshError` with "command not found" message
- Instead of raising error, passes to AI for interpretation
- Returns dummy successful process to suppress error display
- Preserves normal command execution for valid commands

## Design Principles

1. **Simplicity**: Keep the implementation as simple as possible
2. **Non-intrusive**: Don't interfere with normal xonsh operation
3. **Transparency**: Let xonsh handle what it does best
4. **Reliability**: Prefer working with limitations over complex workarounds

## Known Limitations

1. Natural language queries no longer display as errors (Fixed!)
2. No session continuity between queries (Claude CLI limitation)
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
- [ ] Support for additional AI models
  - Architecture ready, need implementations

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
python -m pytest tests/unit/ -v
```

### Local Testing with Claude CLI

```bash
# Test basic functionality
make test

# Test with actual Claude CLI (requires login)
make test-cc

# Run specific integration tests
python -m pytest tests/integration/ -v

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
- Override of `SubprocSpec._run_binary` for command interception
- Modular AI system with pluggable backends
- Smart command filtering to skip common typos
- Direct subprocess integration with AI backends

### Signal Handling
- Shell scripts with `exec` provide cleanest signal handling
- Python subprocess module can interfere with signal propagation
- `os.system()` preserves terminal state better than `subprocess.run()`

## Deployment to PyPI

### Prerequisites (Using PyPI Trusted Publisher)

1. Create a PyPI account at https://pypi.org/account/register/

2. Configure Trusted Publisher on PyPI:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - Project name: `xonai`
     - Repository: `jin0g/xonai`
     - Workflow: `publish.yml`
     - Environment: (leave blank)

PyPI's Trusted Publisher uses OpenID Connect (OIDC) to authenticate GitHub Actions directly - no API tokens needed!

### Deployment Process

1. Update version in `pyproject.toml`
2. Create and push to version branch:
   ```bash
   git checkout -b v0.1.0
   git push origin v0.1.0
   ```
3. GitHub Actions will automatically:
   - Run tests on all platforms and Python versions
   - Build the package
   - Publish to PyPI

### Manual Publishing (if needed)

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Communication Protocol

xonai uses a typed Response object streaming protocol for AI communication.
AI implementations yield `Generator[Response, None, None]`.

### Response Types

1. **InitResponse**: Session start notification
   - `content`: AI name (e.g., "Claude Code")
   - `session_id`: Optional session ID
   - `model`: Optional model name

2. **MessageResponse**: Text messages from AI (streaming support)
   - `content`: Message part or whole
   - `content_type`: MARKDOWN by default

3. **ToolUseResponse**: Tool usage notification
   - `content`: Tool input (command, file path, etc.)
   - `tool`: Tool name (Bash, Read, Edit, etc.)

4. **ToolResultResponse**: Tool execution result
   - `content`: Tool output
   - `tool`: Tool name

5. **ErrorResponse**: Error notification (hidden from users)
   - `content`: Error message
   - `error_type`: Optional error type

6. **ResultResponse**: Session end with statistics
   - `content`: Statistics (duration_ms, cost_usd, etc.)
   - `token`: Token count

### Communication Flow

1. **InitResponse** → Session start
2. **MessageResponse** → AI explanation (optional)
3. **ToolUseResponse** → Tool usage notification
4. **ToolResultResponse** → Tool result (optional)
5. Repeat 3-4 as needed
6. **MessageResponse** → Final answer
7. **ResultResponse** → Session end

### Display Rules

- **InitResponse**: Show after blank line with emoji
- **MessageResponse**: Stream continuously
- **ToolUseResponse**: Show concisely with emoji
- **ToolResultResponse**: Show indented summary
- **ErrorResponse**: Hide from user
- **ResultResponse**: Show statistics after blank line

### Tool-Specific Display

- **Bash** (🔧): Show command, summarize output
- **Read** (📖): Show filename, display line count
- **Edit/Write** (✏️): Show filename, confirm update
- **LS** (📁): Show path, display item count
- **Search/Grep** (🔍): Show pattern, display match count
- **TodoRead** (📋): Show "Reading todos", display count
- **TodoWrite** (📝): Show "Updating todos", confirm
- **WebSearch** (🔍): Show search query
- **WebFetch** (🌐): Show URL