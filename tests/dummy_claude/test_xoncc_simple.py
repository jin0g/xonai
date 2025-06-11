#!/usr/bin/env python3
"""Tests for the simplified xoncc implementation."""

import subprocess
from unittest import mock


class TestXonccSimple:
    """Test the simplified xoncc functionality."""

    @mock.patch("subprocess.run")
    @mock.patch("subprocess.Popen")
    def test_call_claude(self, mock_popen, mock_run):
        """Test calling Claude."""
        from xontrib.xoncc import call_claude_direct

        # Mock 'which claude' to succeed
        mock_run.return_value = mock.Mock(returncode=0)

        # Mock process
        mock_proc = mock.MagicMock()
        mock_proc.stdout = iter(['{"type": "message", "content": "test response"}\n'])
        mock_proc.stderr.read.return_value = ""
        mock_proc.returncode = 0
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        # Call claude
        call_claude_direct("how do I find large files")

        # Verify subprocess.run was called for 'which claude'
        mock_run.assert_called_with(["which", "claude"], capture_output=True, text=True)

        # Verify subprocess.Popen was called with correct command
        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        expected_args = [
            "claude",
            "--print",
            "--verbose",
            "--output-format",
            "stream-json",
            "how do I find large files",
        ]
        assert call_args == expected_args

    @mock.patch("subprocess.run")
    @mock.patch("subprocess.Popen")
    def test_session_resume(self, mock_popen, mock_run):
        """Test session resume functionality."""
        import xontrib.xoncc
        from xontrib.xoncc import call_claude_direct

        # Mock 'which claude' to succeed
        mock_run.return_value = mock.Mock(returncode=0)

        # Set a session ID
        xontrib.xoncc.CC_SESSION_ID = "test-session-123"

        # Mock process
        mock_proc = mock.MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.stderr.read.return_value = ""
        mock_proc.returncode = 0
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        # Call claude
        call_claude_direct("another question")

        # Verify env was set with session ID
        call_kwargs = mock_popen.call_args[1]
        assert "env" in call_kwargs
        assert call_kwargs["env"]["CC_SESSION_ID"] == "test-session-123"

    def test_handle_command_not_found(self):
        """Test command not found handler."""
        from xontrib.xoncc import handle_command_not_found

        # Test with regular command - should call Claude
        with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
            result = handle_command_not_found(["how", "do", "I", "list", "files"])
            assert result is True  # Should return empty dict to suppress error
            mock_claude.assert_called_once_with("how do I list files")

        # Test with claude command - should NOT call Claude (avoid recursion)
        with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
            result = handle_command_not_found(["claude", "--help"])
            assert result is None  # Should return None to let xonsh handle
            mock_claude.assert_not_called()

    def test_natural_language_queries(self):
        """Test natural language detection."""
        from xontrib.xoncc import handle_command_not_found

        # Natural language queries should trigger Claude
        queries = [
            ["How", "do", "I", "find", "large", "files"],
            ["Let's", "search", "for", "python", "files"],
            ["Find", "all", "TODO", "comments"],
            ["What", "is", "the", "git", "command", "to", "undo"],
        ]

        for query in queries:
            with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
                result = handle_command_not_found(query)
                assert result is True
                mock_claude.assert_called_once()

    def test_edge_cases(self):
        """Test edge cases with complex syntax."""
        from xontrib.xoncc import handle_command_not_found

        # Complex syntax that might cause issues
        edge_cases = [
            ["Let's", '"command', "[hello]", '${user}"'],  # Mixed quotes
            ["Find", "files", "with", "spaces in names"],  # Spaces
            ["使い方を教えて"],  # Japanese (single item list)
            ["$VAR=value"],  # Shell variable
        ]

        for case in edge_cases:
            with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
                # Should handle without crashing
                result = handle_command_not_found(case)
                assert result is True
                mock_claude.assert_called_once()

    def test_skip_common_typos(self):
        """Test that common typos are skipped."""
        from xontrib.xoncc import handle_command_not_found

        # Commands that should NOT trigger Claude (exact prefixes)
        skip_commands = [
            ["ls", "-la"],  # Starts with ls
            ["git", "status"],  # Starts with git
            ["python", "script.py"],  # Starts with python
            ["cd", "/tmp"],  # Starts with cd
            ["pwd"],  # Starts with pwd
            ["pip", "install"],  # Starts with pip
        ]

        for cmd in skip_commands:
            with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
                result = handle_command_not_found(cmd)
                assert result is None  # Should return None to let xonsh handle
                mock_claude.assert_not_called()


class TestXonccIntegration:
    """Test xoncc integration with xonsh."""

    def test_xontrib_loading(self):
        """Test that xontrib can be loaded."""
        from xontrib.xoncc import _load_xontrib_

        # Mock xonsh session
        mock_xsh = mock.MagicMock()
        mock_xsh.builtins.events.on_command_not_found = mock.MagicMock()

        # Load xontrib
        result = _load_xontrib_(mock_xsh)

        # Should have patched SubprocSpec._run_binary (function override is primary method)
        # Event handler might or might not be called depending on fallback path
        assert result == {}

    def test_import_in_xonsh(self, tmp_path):
        """Test importing xoncc in xonsh."""
        # Create test script
        test_script = tmp_path / "test_import.xsh"
        test_script.write_text(
            """
# Test that xoncc can be imported
import xoncc

# Try a command that doesn't exist
echo "Testing xoncc"

exit(0)
"""
        )

        # Run in xonsh
        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        # Should work without errors
        assert result.returncode == 0
        assert "Testing xoncc" in result.stdout
