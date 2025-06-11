#!/usr/bin/env python3
"""Tests for the minimal xoncc implementation."""

from unittest import mock


class TestXonccMinimal:
    """Test the minimal xoncc functionality."""

    @mock.patch("subprocess.run")
    @mock.patch("subprocess.Popen")
    def test_call_claude_direct(self, mock_popen, mock_run):
        """Test calling Claude."""
        from xoncc.claude import call_claude_direct

        # Mock 'which claude' to succeed
        mock_run.return_value = mock.Mock(returncode=0)

        # Mock Popen process
        mock_proc = mock.Mock()
        mock_proc.stdout = iter(["test response"])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        # Call claude
        call_claude_direct("how do I find large files")

        # Verify subprocess.Popen was called
        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert "how do I find large files" in str(call_args)

    @mock.patch("subprocess.run")
    @mock.patch("subprocess.Popen")
    def test_session_resume(self, mock_popen, mock_run):
        """Test session resume functionality."""
        import xoncc.claude.cli as cli
        from xoncc.claude import call_claude_direct

        # Set a session ID
        cli.CC_SESSION_ID = "test-session-123"

        # Mock 'which claude' to succeed
        mock_run.return_value = mock.Mock(returncode=0)

        # Mock Popen process
        mock_proc = mock.Mock()
        mock_proc.stdout = iter(["test response"])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        # Call claude
        call_claude_direct("another question")

        # Verify subprocess.Popen was called with session ID in environment
        assert mock_popen.called
        call_kwargs = mock_popen.call_args[1]
        assert "env" in call_kwargs
        assert call_kwargs["env"]["CC_SESSION_ID"] == "test-session-123"

    def test_handle_command_not_found(self):
        """Test command not found handler."""
        from xontrib.xoncc import handle_command_not_found

        # Test with regular command - should call Claude
        with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
            result = handle_command_not_found(["how", "do", "I", "list", "files"])
            assert result is True  # Should return True to suppress error
            mock_claude.assert_called_once_with("how do I list files")

        # Test with claude command - should NOT call Claude (avoid recursion)
        with mock.patch("xontrib.xoncc.call_claude_direct") as mock_claude:
            result = handle_command_not_found(["claude", "--help"])
            assert result is None  # Should return None to let xonsh handle normally
            mock_claude.assert_not_called()

    def test_xontrib_loading(self):
        """Test that xontrib can be loaded."""
        from xoncc.xontrib import _load_xontrib_

        # Mock xonsh session
        mock_xsh = mock.MagicMock()
        mock_xsh.builtins.events.on_command_not_found = mock.MagicMock()

        # Mock the SubprocSpec import
        mock_spec_class = mock.MagicMock()
        mock_spec_class._run_binary = mock.MagicMock()

        with mock.patch("xonsh.procs.specs.SubprocSpec", mock_spec_class):
            # Load xontrib
            result = _load_xontrib_(mock_xsh)

            # Should have attempted to patch SubprocSpec._run_binary
            # The mock setup means we can't verify the actual patching,
            # but we can check the loading succeeded
            # Event handler might or might not be called depending on fallback path
            assert result == {}
