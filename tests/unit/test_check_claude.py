#!/usr/bin/env python3
"""Tests for Claude CLI check functionality."""

from unittest import mock

from xoncc.claude import is_claude_ready, open_claude_docs


class TestClaudeCheck:
    """Test Claude CLI check functions."""

    @mock.patch("subprocess.run")
    def test_is_claude_ready_not_installed(self, mock_run):
        """Test when Claude CLI is not installed."""
        # Mock 'which claude' failing
        mock_run.return_value = mock.Mock(returncode=1)

        ready, status = is_claude_ready()
        assert not ready
        assert status == "not_installed"

    @mock.patch("subprocess.run")
    def test_is_claude_ready_logged_in(self, mock_run):
        """Test when Claude CLI is installed and logged in."""
        # First call: 'which claude' succeeds
        # Second call: 'claude --print /exit' succeeds without auth error
        mock_run.side_effect = [
            mock.Mock(returncode=0),  # which claude
            mock.Mock(returncode=0, stdout="", stderr=""),  # claude command
        ]

        ready, status = is_claude_ready()
        assert ready
        assert status == "ready"

    @mock.patch("subprocess.run")
    def test_is_claude_ready_not_logged_in(self, mock_run):
        """Test when Claude CLI is installed but not logged in."""
        # First call: 'which claude' succeeds
        # Second call: 'claude --print /exit' has auth error
        mock_run.side_effect = [
            mock.Mock(returncode=0),  # which claude
            mock.Mock(returncode=1, stdout="Invalid API key", stderr=""),  # claude command
        ]

        ready, status = is_claude_ready()
        assert not ready
        assert status == "not_logged_in"

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
