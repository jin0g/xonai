#!/usr/bin/env python3
"""Tests for Claude CLI setup functionality."""

import subprocess
from unittest import mock

import pytest

from xoncc.setup_claude import (
    check_claude_cli,
    get_claude_docs_url,
    get_user_language,
)


class TestClaudeSetup:
    """Test Claude CLI setup functions."""

    def test_get_user_language(self):
        """Test language detection."""
        # Mock locale
        with mock.patch("locale.getdefaultlocale") as mock_locale:
            # Test Japanese
            mock_locale.return_value = ("ja_JP.UTF-8", "UTF-8")
            assert get_user_language() == "ja"
            
            # Test English
            mock_locale.return_value = ("en_US.UTF-8", "UTF-8")
            assert get_user_language() == "en"
            
            # Test None
            mock_locale.return_value = (None, None)
            assert get_user_language() == "en"
    
    def test_get_claude_docs_url(self):
        """Test documentation URL selection."""
        with mock.patch("xoncc.setup_claude.get_user_language") as mock_lang:
            # Test Japanese
            mock_lang.return_value = "ja"
            assert get_claude_docs_url() == "https://docs.anthropic.com/ja/docs/claude-code/getting-started"
            
            # Test unsupported language (defaults to English)
            mock_lang.return_value = "ru"
            assert get_claude_docs_url() == "https://docs.anthropic.com/en/docs/claude-code/getting-started"
    
    @mock.patch("subprocess.run")
    def test_check_claude_cli_not_installed(self, mock_run):
        """Test when Claude CLI is not installed."""
        # Mock 'which claude' failing
        mock_run.return_value = mock.Mock(returncode=1)
        
        installed, status = check_claude_cli()
        assert not installed
        assert status == "not_installed"
    
    @mock.patch("subprocess.run")
    def test_check_claude_cli_logged_in(self, mock_run):
        """Test when Claude CLI is installed and logged in."""
        # First call: 'which claude' succeeds
        # Second call: 'claude --print /exit' succeeds
        mock_run.side_effect = [
            mock.Mock(returncode=0),  # which claude
            mock.Mock(returncode=0, stderr=""),  # claude --print /exit
        ]
        
        installed, status = check_claude_cli()
        assert installed
        assert status == "logged_in"
    
    @mock.patch("subprocess.run")
    def test_check_claude_cli_not_logged_in(self, mock_run):
        """Test when Claude CLI is installed but not logged in."""
        # First call: 'which claude' succeeds
        # Second call: 'claude --print /exit' fails with auth error
        mock_run.side_effect = [
            mock.Mock(returncode=0),  # which claude
            mock.Mock(returncode=1, stderr="Invalid API key · Please run /login"),  # claude --print /exit
        ]
        
        installed, status = check_claude_cli()
        assert installed
        assert status == "not_logged_in"