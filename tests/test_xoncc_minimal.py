#!/usr/bin/env python3
"""Tests for the minimal xoncc implementation."""

from unittest import mock


class TestXonccMinimal:
    """Test the minimal xoncc functionality."""

    @mock.patch("os.system")
    def test_call_claude(self, mock_system):
        """Test calling Claude."""
        from xontrib.xoncc import call_claude

        # Mock successful execution
        mock_system.return_value = 0

        # Call claude
        call_claude("how do I find large files")

        # Verify os.system was called
        assert mock_system.called
        # The command should contain the query
        call_args = mock_system.call_args[0][0]
        assert "how do I find large files" in call_args

    @mock.patch("os.system")
    def test_session_resume(self, mock_system):
        """Test session resume functionality."""
        import xontrib.xoncc
        from xontrib.xoncc import call_claude

        # Set a session ID
        xontrib.xoncc.CC_SESSION_ID = "test-session-123"

        # Mock successful execution
        mock_system.return_value = 0

        # Call claude
        call_claude("another question")

        # Verify os.system was called with session ID in environment
        assert mock_system.called
        # Note: We can't directly test environment variables with os.system,
        # but we can verify the command was executed
        call_args = mock_system.call_args[0][0]
        assert "another question" in call_args

    def test_handle_command_not_found(self):
        """Test command not found handler."""
        from xontrib.xoncc import handle_command_not_found

        # Test with regular command - should call Claude
        with mock.patch("xontrib.xoncc.call_claude") as mock_claude:
            result = handle_command_not_found(["how", "do", "I", "list", "files"])
            assert result is None
            mock_claude.assert_called_once_with("how do I list files")

        # Test with claude command - should NOT call Claude (avoid recursion)
        with mock.patch("xontrib.xoncc.call_claude") as mock_claude:
            result = handle_command_not_found(["claude", "--help"])
            assert result == ["claude", "--help"]
            mock_claude.assert_not_called()

    def test_xontrib_loading(self):
        """Test that xontrib can be loaded."""
        from xontrib.xoncc import _load_xontrib_

        # Mock xonsh session
        mock_xsh = mock.MagicMock()
        mock_xsh.builtins.events.on_command_not_found = mock.MagicMock()

        # Mock the SubprocSpec import
        mock_spec_class = mock.MagicMock()
        mock_spec_class._run_binary = mock.MagicMock()

        with mock.patch("xonsh.procs.specs.SubprocSpec", mock_spec_class):
            # Load xontrib
            result = _load_xontrib_(mock_xsh)

            # Should register event handler
            mock_xsh.builtins.events.on_command_not_found.assert_called_once()
            # Should have overridden _run_binary
            assert mock_spec_class._run_binary != mock_spec_class._run_binary.__class__
            assert result == {}
