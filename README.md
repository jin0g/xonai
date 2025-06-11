# xoncc - Xonsh on Claude Code

Automatically ask Claude AI for help when a command is not found in xonsh shell.

## What is this?

xoncc is a simple xonsh extension that catches "command not found" errors and automatically asks Claude AI for help. No special commands needed - just type naturally in any language.

## Installation

1. Install xoncc (includes xonsh automatically):
   ```bash
   pip install xoncc
   ```

2. Install Claude CLI:
   - Download from [Claude AI](https://claude.ai/download)
   - Or follow the [installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

## Usage

### Option 1: Launch with xoncc command (Recommended)
```bash
xoncc
```

### Option 2: Load as xontrib in existing xonsh session
```bash
xonsh
>>> xontrib load xoncc
```

### Option 3: Auto-load in .xonshrc
Add to your `~/.xonshrc`:
```python
xontrib load xoncc
```

## Examples

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

## Quick Start

1. Install: `pip install xoncc`
2. Install Claude CLI (see installation section above)
3. Launch: `xoncc` or in existing xonsh: `xontrib load xoncc`
4. Start asking questions naturally!

## Important Notes

- **xonsh shell only**: This package is designed specifically as a xonsh extension. Python import usage is not supported.
- **Claude CLI required**: You need the Claude CLI installed and accessible in your PATH.
- **Auto-login**: Login to Claude will be handled automatically when needed.

## Requirements

- Python 3.8+
- Claude CLI (automatically prompts for installation if missing)
- xonsh shell (automatically installed with xoncc)

## Development & Technical Details

For development notes, implementation details, and technical documentation, see [CLAUDE.md](CLAUDE.md).

## Status & Roadmap

### ✅ Current Features
- Natural language commands in xonsh shell
- Real-time AI responses with progress display
- Automatic Claude CLI login handling
- Direct AI access with `cc('query')` and `claude('query')`

### 🚧 Planned Features
- Output capture with `$()` syntax
- Pipeline support for natural language queries
- Shell context awareness (history, environment, current directory)
- Parallel AI processing with improved Ctrl+C handling
- AI instruction queuing and parallel execution
- Fullscreen mode compatibility

For detailed technical information and development notes, see [CLAUDE.md](CLAUDE.md).