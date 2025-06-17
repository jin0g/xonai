#!/usr/bin/env python3
"""Claude CLI setup helper functions."""

import locale
import os
import subprocess
import sys


def get_user_language():
    """Get user's language from locale settings."""
    try:
        lang = locale.getdefaultlocale()[0]
        if lang:
            # Extract language code (e.g., 'ja_JP' -> 'ja')
            return lang.split('_')[0].lower()
    except:
        pass
    return 'en'


def get_claude_docs_url():
    """Get appropriate Claude docs URL based on user's language."""
    lang = get_user_language()
    
    # Map of supported languages to their doc URLs
    lang_urls = {
        'ja': 'https://docs.anthropic.com/ja/docs/claude-code/getting-started',
        'ko': 'https://docs.anthropic.com/ko/docs/claude-code/getting-started',
        'zh': 'https://docs.anthropic.com/zh/docs/claude-code/getting-started',
        'es': 'https://docs.anthropic.com/es/docs/claude-code/getting-started',
        'fr': 'https://docs.anthropic.com/fr/docs/claude-code/getting-started',
        'de': 'https://docs.anthropic.com/de/docs/claude-code/getting-started',
        'pt': 'https://docs.anthropic.com/pt/docs/claude-code/getting-started',
    }
    
    # Default to English if language not supported
    return lang_urls.get(lang, 'https://docs.anthropic.com/en/docs/claude-code/getting-started')


def open_claude_docs():
    """Open Claude documentation in browser."""
    url = get_claude_docs_url()
    
    # Try to open URL based on platform
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', url])
    elif sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', url])
    elif sys.platform == 'win32':
        subprocess.run(['start', url], shell=True)
    else:
        print(f"Please visit: {url}")


def check_claude_cli():
    """Check if Claude CLI is installed and logged in."""
    # Check if claude command exists
    try:
        result = subprocess.run(
            ['which', 'claude'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "not_installed"
    except:
        return False, "not_installed"
    
    # Check if logged in using claude --print /exit
    try:
        result = subprocess.run(
            ['claude', '--print', '/exit'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "logged_in"
        else:
            # Check error message for login-related issues
            if "Invalid API key" in result.stderr or "Please run /login" in result.stderr:
                return True, "not_logged_in"
            else:
                return True, "unknown_error"
    except subprocess.TimeoutExpired:
        return True, "timeout"
    except:
        return True, "unknown_error"


def setup_claude_cli():
    """Setup Claude CLI - check installation and login."""
    lang = get_user_language()
    
    # Messages in different languages
    messages = {
        'en': {
            'checking': 'Checking Claude CLI installation...',
            'not_installed': 'Claude CLI is not installed.',
            'opening_docs': 'Opening installation guide...',
            'install_prompt': 'Please install Claude CLI and run xoncc again.',
            'not_logged_in': 'Claude CLI is installed but not logged in.',
            'login_prompt': 'Please login to Claude first:',
            'login_command': '  claude',
            'ready': 'Claude CLI is ready!',
        },
        'ja': {
            'checking': 'Claude CLIのインストールを確認しています...',
            'not_installed': 'Claude CLIがインストールされていません。',
            'opening_docs': 'インストールガイドを開いています...',
            'install_prompt': 'Claude CLIをインストールしてから、xonccを再度実行してください。',
            'not_logged_in': 'Claude CLIはインストールされていますが、ログインしていません。',
            'login_prompt': '最初にClaudeにログインしてください:',
            'login_command': '  claude',
            'ready': 'Claude CLIの準備ができました！',
        },
    }
    
    # Get messages for user's language (default to English)
    msg = messages.get(lang, messages['en'])
    
    print(msg['checking'])
    
    installed, status = check_claude_cli()
    
    if not installed:
        print(f"\n{msg['not_installed']}")
        print(msg['opening_docs'])
        open_claude_docs()
        print(f"\n{msg['install_prompt']}")
        return False
    
    if status == "not_logged_in":
        print(f"\n{msg['not_logged_in']}")
        print(msg['login_prompt'])
        print(msg['login_command'])
        print()
        return False
    
    # If Claude is installed and logged in, we're ready
    print(msg['ready'])
    return True


if __name__ == "__main__":
    # Test the setup
    if setup_claude_cli():
        print("\nClaude CLI is ready to use!")
    else:
        print("\nPlease complete Claude CLI setup.")