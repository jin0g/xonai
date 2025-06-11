# xoncc - Xonsh on Claude Code

## What is this?

xoncc seamlessly integrates Claude Code into your xonsh shell, transforming natural language into shell commands and answers.

## Installation

1. Install Claude Code: [Installation Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

2. Install xoncc:
   ```bash
   pip install xoncc
   ```

## Usage

Launch with xoncc command:
```bash
xoncc
```

## Requirements

- Python 3.9+
- Claude Code
- xonsh shell

## Status & Roadmap

### ✅ Current Features
- [x] Natural language commands in xonsh shell
- [x] Real-time AI responses with progress display
- [x] Automatic Claude Code login handling
- [x] Direct AI access with `cc('query')` and `claude('query')`

### 📋 Planned Features
- [ ] Output capture with `$()` syntax
- [ ] Pipeline support for natural language queries
- [ ] Shell context awareness (history, environment, current directory)
- [ ] Parallel AI processing with improved Ctrl+C handling
- [ ] AI instruction queuing and parallel execution
- [ ] Fullscreen mode compatibility

For detailed technical information and development notes, see [CLAUDE.md](CLAUDE.md).