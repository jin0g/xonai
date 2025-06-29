# xonai - Xonsh Shell on AI Integrations

Transform your xonsh shell with natural language commands. Ask questions, get help, and execute tasks using plain English - xonai seamlessly integrates AI assistance into your terminal workflow.

## Prerequisites

### AI Agent Setup
xonai requires an AI agent to function. Currently supported:

- **Claude Code**: [Installation Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

**Note**: While xonai is designed to support multiple AI models, Claude Code is currently the only available integration.

### System Requirements
- Python 3.9+
- AI agent installed and configured (logged in)

The xonsh shell will be automatically installed as a dependency.

## Installation

```bash
pip install xonai
```

## Usage

Launch xonai to start an AI-enhanced shell:

```bash
xonai
```

Once running, you can use natural language commands alongside regular shell commands:

```bash
# Regular shell commands work as usual
ls -la
cd /home/user

# Natural language queries are processed by AI
how do I find large files
what's the current git status
create a python script to sort a list
```

## Features

### ✅ Available Now
- **Natural Language Commands**: Ask questions and get executable answers
- **Real-time AI Responses**: See AI processing with live progress indicators
- **Rich Terminal Output**: Emoji-based formatting with clear tool indicators
- **Seamless Integration**: Works alongside all your regular shell commands

### 🔜 Coming Soon
- **Multiple AI Models**: Support for additional AI providers
- **Session Memory**: Maintain context across multiple queries
- **Command Capture**: Use AI responses in scripts with `$(ai_query)` syntax
- **Pipeline Support**: Pipe AI responses to other commands
- **Parallel Processing**: Run AI queries in background while using shell

## Troubleshooting

If you encounter issues:
1. Ensure Claude Code is installed and logged in: `claude auth status`
2. Check Python version compatibility (3.9+)
3. Try restarting the shell after installation

For development documentation, see [DEVELOPMENT.md](DEVELOPMENT.md).

## License

MIT License
