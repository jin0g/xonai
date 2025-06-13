"""Tests for the display module."""

from xonai.ai import (
    ContentType,
    ErrorResponse,
    ErrorType,
    InitResponse,
    MessageResponse,
    ResultResponse,
    ToolResultResponse,
    ToolUseResponse,
)
from xonai.display import ResponseFormatter


class TestResponseFormatter:
    """Test the ResponseFormatter functionality."""

    def test_message_response(self, capsys):
        """Test streaming message content."""
        formatter = ResponseFormatter()
        response = MessageResponse(content="Hello world")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "Hello world"  # Streaming text prints without newline

    def test_init_response(self, capsys):
        """Test INIT message formatting."""
        formatter = ResponseFormatter()
        response = InitResponse(
            content="Claude Code", session_id="1234567890abcdef", model="claude-sonnet-4-20250514"
        )
        formatter.format(response)

        captured = capsys.readouterr()
        assert (
            captured.out == "🚀 Claude Code: model=claude-sonnet-4-20250514, id=1234567890abcdef\n"
        )

    def test_tool_use_bash(self, capsys):
        """Test Bash tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="ls -la", tool="Bash")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🔧 ls -la\n"

    def test_tool_use_read(self, capsys):
        """Test Read tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="/home/user/file.txt", tool="Read")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "📖 /home/user/file.txt\n"

    def test_tool_use_todo_write(self, capsys):
        """Test TodoWrite tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="TodoWrite", tool="TodoWrite")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "📝 TodoWrite\n"

    def test_tool_result_empty(self, capsys):
        """Test empty tool results."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="", tool="Bash")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "(empty output)\n"

    def test_tool_result_shown(self, capsys):
        """Test tool results are shown with tool name."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="Line 1\nLine 2\nLine 3", tool="Bash")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "[Bash] Line 1\nLine 2\nLine 3\n"

    def test_result_response(self, capsys):
        """Test result summary formatting."""
        formatter = ResponseFormatter()
        response = ResultResponse(
            content="duration_ms=5500, cost_usd=0.005000, input_tokens=1000, output_tokens=500",
            token=1500,
        )
        formatter.format(response)

        captured = capsys.readouterr()
        expected = (
            "\n📊 duration_ms=5500, cost_usd=0.005000, "
            "input_tokens=1000, output_tokens=500, next_session_tokens=1,500\n"
        )
        assert captured.out == expected

    def test_error_response(self, capsys):
        """Test error message formatting."""
        formatter = ResponseFormatter()
        response = ErrorResponse(content="Something went wrong", error_type=None)
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "\n❌ Something went wrong\n"

    def test_streaming_text_with_newline(self, capsys):
        """Test multiple streaming messages."""
        formatter = ResponseFormatter()

        # First streaming message
        formatter.format(MessageResponse(content="Hello "))
        # Second streaming message
        formatter.format(MessageResponse(content="world\n"))
        # Non-streaming message should be on new line
        formatter.format(ErrorResponse(content="Error"))

        captured = capsys.readouterr()
        assert captured.out == "Hello world\n\n❌ Error\n"

    def test_tool_use_ls_with_ignore(self, capsys):
        """Test LS tool with ignore parameter formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(
            content="/Users/akira/xonai (ignore: venv, htmlcov, *.egg-info)", tool="LS"
        )
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "📁 /Users/akira/xonai (ignore: venv, htmlcov, *.egg-info)\n"

    def test_tool_use_websearch(self, capsys):
        """Test WebSearch tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="site:pypi.org xonai", tool="WebSearch")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🔍 site:pypi.org xonai\n"

    def test_error_types(self, capsys):
        """Test error response with different error types."""
        formatter = ResponseFormatter()

        # Test with NOT_LOGGED_IN error type
        response = ErrorResponse(
            content="Please log in to Claude CLI", error_type=ErrorType.NOT_LOGGED_IN
        )
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "\n❌ Please log in to Claude CLI\n"

        # Test with None error type (unexpected error)
        formatter = ResponseFormatter()
        response = ErrorResponse(content="Unexpected error occurred", error_type=None)
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "\n❌ Unexpected error occurred\n"

    def test_content_type_defaults(self):
        """Test content type defaults for different response types."""
        # MessageResponse defaults to MARKDOWN
        msg = MessageResponse(content="Hello")
        assert msg.content_type == ContentType.MARKDOWN

        # Other responses default to TEXT
        init = InitResponse(content="Claude Code")
        assert init.content_type == ContentType.TEXT

        tool = ToolUseResponse(content="Tool", tool="Generic")
        assert tool.content_type == ContentType.TEXT

        result = ToolResultResponse(content="Result", tool="Bash")
        assert result.content_type == ContentType.TEXT

        error = ErrorResponse(content="Error")
        assert error.content_type == ContentType.TEXT

        final = ResultResponse(content="stats", token=100)
        assert final.content_type == ContentType.TEXT
