#!/usr/bin/env python3
"""Tests for tool formatting utilities"""

from xoncc.formatters.tools import ToolFormatter


class TestToolFormatter:
    """Test cases for ToolFormatter class"""

    def test_format_tool_use_todo_read(self):
        """Test formatting TodoRead tool with no input"""
        data = {"type": "tool_use", "name": "TodoRead", "input": {}}
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ TodoRead\n"

    def test_format_tool_use_with_description(self):
        """Test formatting tool with description"""
        data = {
            "type": "tool_use",
            "name": "Bash",
            "input": {"command": "ls -la", "description": "List all files"},
        }
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ Bash: List all files\n"

    def test_format_tool_use_task(self):
        """Test formatting Task tool"""
        data = {
            "type": "tool_use",
            "name": "Task",
            "input": {"prompt": "Search for files", "description": "Find Python files"},
        }
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ Task: Find Python files\n"

    def test_format_tool_use_with_query(self):
        """Test formatting tool with query"""
        data = {
            "type": "tool_use",
            "name": "WebSearch",
            "input": {"query": "Python testing best practices"},
        }
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ WebSearch: Python testing best practices\n"

    def test_format_tool_use_bash_no_description(self):
        """Test formatting Bash tool without description"""
        data = {"type": "tool_use", "name": "Bash", "input": {"command": "echo 'Hello World'"}}
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ Bash: echo 'Hello World'\n"

    def test_format_tool_use_bash_long_command(self):
        """Test formatting Bash tool with long command"""
        long_cmd = "find . -name '*.py' -type f -exec grep -l 'test' {} + | head -20"
        data = {"type": "tool_use", "name": "Bash", "input": {"command": long_cmd}}
        result = ToolFormatter.format_tool_use(data)
        # Since the command is > 50 chars, it should be truncated
        assert result.startswith("⏺ Bash: ")
        assert result.endswith("...\n")
        assert len(result) < len("⏺ Bash: " + long_cmd + "\n")

    def test_format_tool_use_with_file_path(self):
        """Test formatting tool with file path"""
        data = {"type": "tool_use", "name": "Read", "input": {"file_path": "/path/to/file.py"}}
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ Read: /path/to/file.py\n"

    def test_format_tool_use_with_pattern(self):
        """Test formatting tool with pattern"""
        data = {"type": "tool_use", "name": "Glob", "input": {"pattern": "**/*.test.py"}}
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ Glob: **/*.test.py\n"

    def test_format_tool_use_todo_write(self):
        """Test formatting TodoWrite tool"""
        data = {
            "type": "tool_use",
            "name": "TodoWrite",
            "input": {
                "todos": [
                    {"content": "Task 1", "status": "pending"},
                    {"content": "Task 2", "status": "completed"},
                ]
            },
        }
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ TodoWrite: 2 todos\n"

    def test_format_tool_use_todo_write_single(self):
        """Test formatting TodoWrite tool with single todo"""
        data = {
            "type": "tool_use",
            "name": "TodoWrite",
            "input": {"todos": [{"content": "Task 1", "status": "pending"}]},
        }
        result = ToolFormatter.format_tool_use(data)
        assert result == "⏺ TodoWrite: 1 todo\n"

    def test_format_tool_use_invalid_type(self):
        """Test formatting with invalid type"""
        data = {"type": "other", "name": "Test"}
        result = ToolFormatter.format_tool_use(data)
        assert result is None

    def test_format_tool_result_success(self):
        """Test formatting successful tool result"""
        data = {"type": "tool_result", "content": "Operation completed successfully"}
        result = ToolFormatter.format_tool_result(data)
        assert result == "  ⎿ Operation completed successfully\n"

    def test_format_tool_result_error(self):
        """Test formatting error tool result"""
        data = {"type": "tool_result", "is_error": True, "content": "File not found"}
        result = ToolFormatter.format_tool_result(data)
        assert result == "  ⎿ Error: File not found\n"

    def test_format_tool_result_long_content(self):
        """Test formatting tool result with long content"""
        long_content = "A" * 250
        data = {"type": "tool_result", "content": long_content}
        result = ToolFormatter.format_tool_result(data)
        assert result == f"  ⎿ {'A' * 197}...\n"

    def test_format_tool_result_empty_content(self):
        """Test formatting tool result with empty content"""
        data = {"type": "tool_result", "content": ""}
        result = ToolFormatter.format_tool_result(data)
        assert result is None

    def test_format_tool_result_invalid_type(self):
        """Test formatting with invalid type"""
        data = {"type": "other", "content": "Test"}
        result = ToolFormatter.format_tool_result(data)
        assert result is None

    def test_format_thinking(self):
        """Test formatting thinking block"""
        data = {"type": "thinking", "content": "Analyzing the problem..."}
        result = ToolFormatter.format_thinking(data)
        assert result == "💭 Analyzing the problem...\n"

    def test_format_thinking_long_content(self):
        """Test formatting thinking block with long content"""
        long_thinking = "This is a very long thinking process " * 10
        data = {"type": "thinking", "content": long_thinking}
        result = ToolFormatter.format_thinking(data)
        assert result.startswith("💭 ")
        assert result.endswith("...\n")
        assert len(result) < 110  # 100 chars + emoji + ellipsis + newline

    def test_format_thinking_empty(self):
        """Test formatting thinking block with empty content"""
        data = {"type": "thinking", "content": "   "}
        result = ToolFormatter.format_thinking(data)
        assert result is None

    def test_format_thinking_invalid_type(self):
        """Test formatting with invalid type"""
        data = {"type": "other", "content": "Test"}
        result = ToolFormatter.format_thinking(data)
        assert result is None
