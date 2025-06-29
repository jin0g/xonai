"""Test various Claude CLI JSON response patterns."""

import json
from unittest.mock import Mock, patch

from xonai.ai.base import (
    ErrorResponse,
    ErrorType,
    MessageResponse,
    ToolResultResponse,
    ToolUseResponse,
)
from xonai.ai.claude import ClaudeAI


class TestClaudeJSONPatterns:
    """Test various JSON patterns from Claude CLI."""

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_nested_tool_use_content(self, mock_which, mock_popen):
        """Test nested tool_use content patterns."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Complex nested structure - Claude sends these as separate messages
        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init", "model": "claude-3"}),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {"content": [{"type": "text", "text": "Let me help you."}]},
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Bash",
                                "input": {
                                    "command": "ls -la | grep test",
                                    "description": "List test files",
                                },
                            }
                        ]
                    },
                }
            ),
            json.dumps({"type": "result", "usage": {"total_tokens": 50}}),
        ]

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter([])
        mock_proc.wait.return_value = 0

        ai = ClaudeAI()
        responses = list(ai("test"))

        # Verify responses
        assert len(responses) >= 3
        tool_uses = [r for r in responses if isinstance(r, ToolUseResponse)]
        assert len(tool_uses) == 1
        assert tool_uses[0].tool == "Bash"
        assert "ls -la | grep test" in tool_uses[0].content

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_error_not_logged_in(self, mock_which, mock_popen):
        """Test NOT_LOGGED_IN error detection."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        mock_proc.stdout = iter([])
        mock_proc.stderr = iter(["Error: You are not logged in to Claude\n"])
        mock_proc.wait.return_value = 1

        ai = ClaudeAI()
        responses = list(ai("test"))

        errors = [r for r in responses if isinstance(r, ErrorResponse)]
        assert len(errors) == 1
        assert errors[0].error_type == ErrorType.NOT_LOGGED_IN

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_network_error_detection(self, mock_which, mock_popen):
        """Test network error detection."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        mock_proc.stdout = iter([])
        mock_proc.stderr = iter(["Connection timeout: Unable to reach API\n"])
        mock_proc.wait.return_value = 1

        ai = ClaudeAI()
        responses = list(ai("test"))

        errors = [r for r in responses if isinstance(r, ErrorResponse)]
        assert len(errors) == 1
        assert errors[0].error_type == ErrorType.NETWORK_ERROR

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_malformed_json_recovery(self, mock_which, mock_popen):
        """Test recovery from malformed JSON."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init"}),
            '{"type": "content_block_delta", "delta": {"text": "Hello',  # Incomplete JSON
            '{"type": "content_block_delta", "delta": {"text": " world"}}',
            json.dumps({"type": "result", "usage": {"total_tokens": 10}}),
        ]

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter([])
        mock_proc.wait.return_value = 0

        ai = ClaudeAI()
        responses = list(ai("test"))

        # Should recover and process valid lines
        messages = [r for r in responses if isinstance(r, MessageResponse)]
        assert len(messages) == 1
        assert "world" in messages[0].content

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_empty_tool_result(self, mock_which, mock_popen):
        """Test empty tool result handling."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init"}),
            json.dumps(
                {"type": "user", "message": {"content": [{"type": "tool_result", "content": ""}]}}
            ),
            json.dumps({"type": "result", "usage": {"total_tokens": 10}}),
        ]

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter([])
        mock_proc.wait.return_value = 0

        ai = ClaudeAI()
        responses = list(ai("test"))

        tool_results = [r for r in responses if isinstance(r, ToolResultResponse)]
        assert len(tool_results) == 1
        assert tool_results[0].content == ""

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_multiple_tools_sequence(self, mock_which, mock_popen):
        """Test multiple tools in sequence."""
        mock_which.return_value = "/usr/bin/claude"
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init"}),
            # First tool
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Read",
                                "input": {"file_path": "/test.txt"},
                            }
                        ]
                    },
                }
            ),
            # Tool result
            json.dumps(
                {
                    "type": "user",
                    "message": {"content": [{"type": "tool_result", "content": "file contents"}]},
                }
            ),
            # Second tool
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Edit",
                                "input": {
                                    "file_path": "/test.txt",
                                    "old_string": "old",
                                    "new_string": "new",
                                },
                            }
                        ]
                    },
                }
            ),
            json.dumps({"type": "result", "usage": {"total_tokens": 100}}),
        ]

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter([])
        mock_proc.wait.return_value = 0

        ai = ClaudeAI()
        responses = list(ai("test"))

        # Check tool sequence
        tool_uses = [r for r in responses if isinstance(r, ToolUseResponse)]
        assert len(tool_uses) == 2
        assert tool_uses[0].tool == "Read"
        assert tool_uses[1].tool == "Edit"
