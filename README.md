# xonai - Xonsh Shell on AI Integrations

xonai seamlessly integrates AI assistants into your xonsh shell, transforming natural language into shell commands and answers. Currently supports Claude AI with a modular architecture for future AI models.

## Prerequisites

### AI Agent Setup
xonai requires an AI agent to function. Currently supported:

- **Claude Code** (Primary): [Installation Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

**Note**: While xonai is designed with a modular architecture to support multiple AI models in the future, Claude Code is currently the only supported AI agent.

### System Requirements
- Python 3.9+
- The AI agent must be installed and properly configured (logged in)

**Note**: xonsh shell will be automatically installed as a dependency.

## Installation

```bash
pip install xonai
```

## Usage

Launch with xonai command:
```bash
xonai
```

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

## License

MIT License - Free for personal and commercial use.
