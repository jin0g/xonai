# xonai - AI Integration for Xonsh Shell

## What is this?

xonai seamlessly integrates AI assistants into your xonsh shell, transforming natural language into shell commands and answers. Currently supports Claude AI with a modular architecture for future AI models.

## Installation

1. Install Claude Code: [Installation Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

2. Install xonai:
   ```bash
   pip install xonai
   ```

## Usage

Launch with xonai command:
```bash
xonai
```

## Requirements

- Python 3.9+
- Claude Code (logged in)
- xonsh shell

## Status & Roadmap

### ✅ Current Features
- [x] Natural language commands in xonsh shell
- [x] Real-time AI responses with progress display
- [x] Emoji-rich output formatting with tool indicators
- [x] Modular AI architecture (supports multiple AI models)

### 📋 Planned Features
- [ ] Markdown syntax highlighting and colorization
- [ ] Detailed tool results display
- [ ] Session continuity across queries
- [ ] Capture with `$()` syntax
- [ ] Pipeline support for natural language queries
- [ ] Parallel AI processing
