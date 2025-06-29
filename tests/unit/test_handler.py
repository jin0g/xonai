"""Test xonai command handler functionality."""

import os
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

# Mock xonsh if not available
try:
    import xonsh.tools as xt
except ImportError:
    # Create mock for test environment
    class MockXonshError(Exception):
        pass

    xt = type("MockXonshTools", (), {"XonshError": MockXonshError})()

from xonai.ai.base import InitResponse, MessageResponse
from xonai.handler import (
    create_dummy_process,
    get_ai_instance,
    process_natural_language_query,
    should_skip_command,
    xonai_run_binary_handler,
)


class TestHandler:
    """Test xonai command handler functions."""

    def test_get_ai_instance_claude(self):
        """Test getting Claude AI instance."""
        with patch.dict(os.environ, {}, clear=True):
            ai = get_ai_instance()
            assert ai.__class__.__name__ == "ClaudeAI"

    def test_get_ai_instance_dummy(self):
        """Test getting DummyAI instance when XONAI_DUMMY=1."""
        with patch.dict(os.environ, {"XONAI_DUMMY": "1"}):
            ai = get_ai_instance()
            assert ai.__class__.__name__ == "DummyAI"

    @patch("xonai.handler.get_ai_instance")
    @patch("xonai.handler.ResponseFormatter")
    def test_process_natural_language_query(self, mock_formatter_class, mock_get_ai):
        """Test processing natural language query."""
        # Setup mocks
        mock_ai = Mock()
        mock_ai.return_value = [
            InitResponse(content="Test AI"),
            MessageResponse(content="Hello"),
        ]
        mock_get_ai.return_value = mock_ai

        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter

        # Test
        process_natural_language_query("test query")

        # Verify
        mock_ai.assert_called_once_with("test query")
        assert mock_formatter.format.call_count == 2

    def test_should_skip_command_empty_args(self):
        """Test skipping empty args."""
        assert should_skip_command([]) is True

    def test_should_skip_command_known_commands(self):
        """Test skipping known commands."""
        skip_commands = ["ls", "cd", "pwd", "git", "python", "pip", "claude"]

        for cmd in skip_commands:
            assert should_skip_command([cmd]) is True
            assert should_skip_command([cmd, "arg1", "arg2"]) is True

    def test_should_skip_command_partial_match(self):
        """Test skipping commands that start with known prefixes."""
        assert should_skip_command(["ls-la"]) is True  # starts with "ls"
        assert should_skip_command(["git-status"]) is True  # starts with "git"
        assert should_skip_command(["python3"]) is True  # starts with "python"

    def test_should_skip_command_natural_language(self):
        """Test not skipping natural language queries."""
        natural_queries = [
            ["how", "do", "I", "list", "files"],
            ["what", "is", "the", "current", "directory"],
            ["help", "me", "with", "git"],
            ["create", "a", "python", "script"],
        ]

        for query in natural_queries:
            assert should_skip_command(query) is False

    @patch("subprocess.Popen")
    def test_create_dummy_process_unix(self, mock_popen):
        """Test creating dummy process on Unix."""
        with patch.object(sys, "platform", "linux"):
            mock_process = Mock()
            mock_popen.return_value = mock_process

            result = create_dummy_process()

            mock_popen.assert_called_once_with(
                ["true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            assert result == mock_process

    @patch("subprocess.Popen")
    def test_create_dummy_process_windows(self, mock_popen):
        """Test creating dummy process on Windows."""
        with patch.object(sys, "platform", "win32"):
            mock_process = Mock()
            mock_popen.return_value = mock_process

            result = create_dummy_process()

            mock_popen.assert_called_once_with(
                ["cmd", "/c", "exit", "0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            assert result == mock_process

    @patch("xonai.handler.create_dummy_process")
    @patch("xonai.handler.process_natural_language_query")
    @patch("xonai.handler.should_skip_command")
    def test_xonai_run_binary_handler_success(
        self, mock_should_skip, mock_process_query, mock_create_dummy
    ):
        """Test successful command execution."""
        # Setup
        original_method = Mock()
        subprocess_spec = Mock()
        kwargs = {"test": "kwargs"}
        expected_result = Mock()
        original_method.return_value = expected_result

        # Test
        result = xonai_run_binary_handler(original_method, subprocess_spec, kwargs)

        # Verify
        original_method.assert_called_once_with(subprocess_spec, kwargs)
        assert result == expected_result
        mock_should_skip.assert_not_called()
        mock_process_query.assert_not_called()
        mock_create_dummy.assert_not_called()

    @patch("xonai.handler.create_dummy_process")
    @patch("xonai.handler.process_natural_language_query")
    @patch("xonai.handler.should_skip_command")
    def test_xonai_run_binary_handler_skip_command(
        self, mock_should_skip, mock_process_query, mock_create_dummy
    ):
        """Test skipping command that should show normal error."""

        # Setup
        original_method = Mock()
        original_method.side_effect = xt.XonshError("command not found: ls")

        subprocess_spec = Mock()
        subprocess_spec.args = ["ls", "-la"]

        mock_should_skip.return_value = True
        kwargs = {}

        # Test - should re-raise the exception
        with patch.object(sys.modules["xonai.handler"], "xt", xt, create=True):
            with pytest.raises(xt.XonshError):
                xonai_run_binary_handler(original_method, subprocess_spec, kwargs)

        # Verify
        mock_should_skip.assert_called_once_with(["ls", "-la"])
        mock_process_query.assert_not_called()
        mock_create_dummy.assert_not_called()

    @patch("xonai.handler.create_dummy_process")
    @patch("xonai.handler.process_natural_language_query")
    @patch("xonai.handler.should_skip_command")
    def test_xonai_run_binary_handler_natural_language(
        self, mock_should_skip, mock_process_query, mock_create_dummy
    ):
        """Test processing natural language command."""

        # Setup
        original_method = Mock()
        original_method.side_effect = xt.XonshError("command not found: how do I list files")

        subprocess_spec = Mock()
        subprocess_spec.args = ["how", "do", "I", "list", "files"]

        mock_should_skip.return_value = False
        mock_dummy_process = Mock()
        mock_create_dummy.return_value = mock_dummy_process
        kwargs = {}

        # Test
        with patch.object(sys.modules["xonai.handler"], "xt", xt, create=True):
            result = xonai_run_binary_handler(original_method, subprocess_spec, kwargs)

        # Verify
        mock_should_skip.assert_called_once_with(["how", "do", "I", "list", "files"])
        mock_process_query.assert_called_once_with("how do I list files")
        mock_create_dummy.assert_called_once()
        assert result == mock_dummy_process

    def test_xonai_run_binary_handler_other_error(self):
        """Test re-raising non-command-not-found errors."""

        # Setup
        original_method = Mock()
        original_method.side_effect = xt.XonshError("some other error")
        subprocess_spec = Mock()
        kwargs = {}

        # Test - should re-raise the exception
        with patch.object(sys.modules["xonai.handler"], "xt", xt, create=True):
            with pytest.raises(xt.XonshError) as exc_info:
                xonai_run_binary_handler(original_method, subprocess_spec, kwargs)

        assert "some other error" in str(exc_info.value)

    def test_xonai_run_binary_handler_no_args(self):
        """Test handling subprocess_spec without args."""

        # Setup
        original_method = Mock()
        original_method.side_effect = xt.XonshError("command not found")
        subprocess_spec = Mock()
        subprocess_spec.args = None  # No args
        kwargs = {}

        # Test - should re-raise since no args to process
        with patch.object(sys.modules["xonai.handler"], "xt", xt, create=True):
            with pytest.raises(xt.XonshError):
                xonai_run_binary_handler(original_method, subprocess_spec, kwargs)
