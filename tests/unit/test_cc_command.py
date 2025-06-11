#!/usr/bin/env python3
"""Tests for cc command"""

from unittest import mock

import pytest


class TestCCCommand:
    """Test the cc command functionality."""

    @mock.patch("subprocess.run")
    @mock.patch("pathlib.Path.exists")
    def test_cc_command_success(self, mock_exists, mock_run):
        """Test successful cc command execution."""
        from xoncc.cc import cc_command

        # Mock script exists
        mock_exists.return_value = True

        # Mock successful shell script execution
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Mock sys.exit to prevent actual exit
        with mock.patch("sys.exit") as mock_exit:
            cc_command()

            # Verify shell script was called
            mock_run.assert_called_once()
            # Verify exit was called with success code
            mock_exit.assert_called_once_with(0)

    @mock.patch("subprocess.run")
    @mock.patch("pathlib.Path.exists")
    def test_cc_command_claude_error(self, mock_exists, mock_run):
        """Test cc command when shell script fails."""
        from xoncc.cc import cc_command

        # Mock script exists
        mock_exists.return_value = True

        # Mock shell script failure
        mock_result = mock.MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        with mock.patch("sys.exit") as mock_exit:
            cc_command()
            # Verify exit was called with error code
            mock_exit.assert_called_once_with(1)

    @mock.patch("pathlib.Path.exists")
    def test_cc_command_no_script(self, mock_exists):
        """Test cc command when script doesn't exist."""
        from xoncc.cc import cc_command

        # Mock script doesn't exist
        mock_exists.return_value = False

        with mock.patch("sys.exit") as mock_exit:
            with mock.patch("builtins.print"):
                cc_command()
                # Verify exit was called with error code (may be called twice)
                assert mock_exit.call_count >= 1
                assert 1 in [call.args[0] for call in mock_exit.call_args_list]

    @mock.patch("subprocess.run")
    @mock.patch("pathlib.Path.exists")
    def test_cc_command_exception(self, mock_exists, mock_run):
        """Test cc command when subprocess raises exception."""
        from xoncc.cc import cc_command

        # Mock script exists
        mock_exists.return_value = True

        # Mock subprocess exception
        mock_run.side_effect = Exception("Test error")

        with mock.patch("sys.exit") as mock_exit:
            with mock.patch("builtins.print"):
                cc_command()
                # Verify exit was called with error code (may be called twice)
                assert mock_exit.call_count >= 1
                assert 1 in [call.args[0] for call in mock_exit.call_args_list]

    def test_extract_session_id(self):
        """Test session ID extraction from JSON output."""
        # extract_session_id function was removed, skip this test
        pytest.skip("extract_session_id function removed")

    def test_extract_session_id_no_session(self):
        """Test session ID extraction when no session ID present."""
        # extract_session_id function was removed, skip this test
        pytest.skip("extract_session_id function removed")

    def test_extract_session_id_invalid_json(self):
        """Test session ID extraction with invalid JSON."""
        # extract_session_id function was removed, skip this test
        pytest.skip("extract_session_id function removed")
