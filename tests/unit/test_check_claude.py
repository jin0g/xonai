#!/usr/bin/env python3
"""Tests for Claude CLI check functionality."""

from unittest import mock

from xonai.agents.claude import open_claude_docs


class TestClaudeCheck:
    """Test Claude CLI check functions."""

    @mock.patch("subprocess.run")
    @mock.patch("sys.platform", "darwin")
    def test_open_claude_docs_macos(self, mock_run):
        """Test opening docs on macOS."""
        open_claude_docs()
        mock_run.assert_called_once_with(
            ["open", "https://docs.anthropic.com/en/docs/claude-code/getting-started"]
        )

    @mock.patch("subprocess.run")
    @mock.patch("sys.platform", "linux")
    def test_open_claude_docs_linux(self, mock_run):
        """Test opening docs on Linux."""
        open_claude_docs()
        mock_run.assert_called_once_with(
            ["xdg-open", "https://docs.anthropic.com/en/docs/claude-code/getting-started"]
        )
