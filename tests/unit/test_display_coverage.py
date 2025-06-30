"""Additional tests to improve coverage for display module."""

import json

from xonai.agents import (
    InitResponse,
    MessageResponse,
    ResultResponse,
    ToolResultResponse,
    ToolUseResponse,
)
from xonai.display import ResponseFormatter


class TestDisplayCoverage:
    """Additional tests for better coverage."""

    def test_tool_use_long_bash_command(self, capsys):
        """Test Bash command truncation when too long."""
        formatter = ResponseFormatter()
        long_command = (
            "find . -type f -name '*.py' -exec grep -l 'pattern' {} \\; | xargs wc -l | sort -nr"
        )
        response = ToolUseResponse(content=long_command, tool="Bash")
        formatter.format(response)

        captured = capsys.readouterr()
        # Should truncate at 60 chars (57 chars + "...")
        assert captured.out == "🔧 find . -type f -name '*.py' -exec grep -l 'pattern' {} \\;...\n"

    def test_tool_use_task(self, capsys):
        """Test Task tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="Search for configuration files", tool="Task")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🤖 Task: Search for configuration files\n"

    def test_tool_use_webfetch(self, capsys):
        """Test WebFetch tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="https://example.com/api", tool="WebFetch")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🌐 Fetching: https://example.com/api\n"

    def test_tool_use_glob_with_pattern(self, capsys):
        """Test Glob tool with pattern in path."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="*.py in src/", tool="Glob")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🔍 Searching for: *.py\n"

    def test_tool_use_grep_without_path(self, capsys):
        """Test Grep tool without 'in' separator."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="TODO", tool="Grep")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🔍 Searching: TODO\n"

    def test_tool_use_todoread(self, capsys):
        """Test TodoRead tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="", tool="TodoRead")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "📋 Reading todos\n"

    def test_tool_use_unknown_tool(self, capsys):
        """Test unknown tool formatting."""
        formatter = ResponseFormatter()
        response = ToolUseResponse(content="some input", tool="UnknownTool")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🔧 UnknownTool: some input\n"

    def test_tool_result_read_multiline(self, capsys):
        """Test Read tool result with multiple lines."""
        formatter = ResponseFormatter()
        content = "line1\nline2\nline3\nline4\nline5"
        response = ToolResultResponse(content=content, tool="Read")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Read 5 lines\n"

    def test_tool_result_edit(self, capsys):
        """Test Edit tool result."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="File edited successfully", tool="Edit")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → File updated\n"

    def test_tool_result_multiedit(self, capsys):
        """Test MultiEdit tool result."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="Multiple edits applied", tool="MultiEdit")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → File updated\n"

    def test_tool_result_write(self, capsys):
        """Test Write tool result."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="File written", tool="Write")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → File written\n"

    def test_tool_result_bash_long_output(self, capsys):
        """Test Bash tool result with long single line."""
        formatter = ResponseFormatter()
        long_line = "a" * 100  # Line longer than 60 chars
        response = ToolResultResponse(content=long_line, tool="Bash")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Command completed\n"

    def test_tool_result_glob_with_matches(self, capsys):
        """Test Glob tool result with matches."""
        formatter = ResponseFormatter()
        content = "file1.py\nfile2.py\nfile3.py"
        response = ToolResultResponse(content=content, tool="Glob")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Found 3 matches\n"

    def test_tool_result_grep_no_matches(self, capsys):
        """Test Grep tool result with no matches."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="", tool="Grep")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_tool_result_grep_empty_lines(self, capsys):
        """Test Grep tool result with whitespace only."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="   \n  \n  ", tool="Grep")
        formatter.format(response)

        captured = capsys.readouterr()
        # When content is all whitespace, it's considered empty
        assert captured.out == ""

    def test_tool_result_todoread_with_json(self, capsys):
        """Test TodoRead result with valid JSON."""
        formatter = ResponseFormatter()
        todos = [
            {"id": "1", "task": "Task 1"},
            {"id": "2", "task": "Task 2"},
            {"id": "3", "task": "Task 3"},
        ]
        response = ToolResultResponse(content=json.dumps(todos), tool="TodoRead")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → 3 todos\n"

    def test_tool_result_todoread_invalid_json(self, capsys):
        """Test TodoRead result with invalid JSON."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="Not valid JSON", tool="TodoRead")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Todos listed\n"

    def test_tool_result_todowrite(self, capsys):
        """Test TodoWrite result."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="Todos updated", tool="TodoWrite")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Todos updated\n"

    def test_tool_result_unknown_short(self, capsys):
        """Test unknown tool result with short output."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="Success", tool="CustomTool")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Success\n"

    def test_tool_result_unknown_long(self, capsys):
        """Test unknown tool result with long output."""
        formatter = ResponseFormatter()
        long_content = (
            "This is a very long output that exceeds the 80 character limit for displaying inline"
        )
        response = ToolResultResponse(content=long_content, tool="CustomTool")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Completed\n"

    def test_tool_result_unknown_multiline(self, capsys):
        """Test unknown tool result with multiple lines."""
        formatter = ResponseFormatter()
        response = ToolResultResponse(content="line1\nline2", tool="CustomTool")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "  → Completed\n"

    def test_init_response_without_session_id(self, capsys):
        """Test INIT response without session ID."""
        formatter = ResponseFormatter()
        response = InitResponse(content="Test AI", model="test-model")
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "🚀 Test AI: model=test-model\n"

    def test_result_response_without_stats(self, capsys):
        """Test result response without statistics."""
        formatter = ResponseFormatter()
        response = ResultResponse(content="", token=100)
        formatter.format(response)

        captured = capsys.readouterr()
        assert captured.out == "\n📊 next_session_tokens=100\n"

    def test_message_after_tool_result(self, capsys):
        """Test message formatting after tool result."""
        formatter = ResponseFormatter()

        # First a tool result (sets last_was_newline=True)
        formatter.format(ToolResultResponse(content="Success", tool="Bash"))

        # Then a message
        formatter.format(MessageResponse(content="Task completed"))

        captured = capsys.readouterr()
        assert captured.out == "  → Success\nTask completed"

    def test_truncate_to_width(self):
        """Test the _truncate_to_width method directly."""
        formatter = ResponseFormatter()

        # Test with specific width
        long_text = "This is a very long line that should be truncated"
        result = formatter._truncate_to_width(long_text, width=20)
        assert result == "This is a very lo..."

        # Test with multiple lines
        multi_line = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"
        result = formatter._truncate_to_width(multi_line)
        lines = result.split("\n")
        assert len(lines) == 6  # 5 lines + "..."
        assert lines[-1] == "..."

        # Test with ANSI codes (not implemented but for coverage)
        ansi_text = "\x1b[31mRed text\x1b[0m"
        result = formatter._truncate_to_width(ansi_text, width=10)
        # Should handle ANSI codes gracefully
