#!/usr/bin/env python3
"""Tests for log formatter"""

import json

from xoncc.formatters.log import (
    format_assistant_message,
    format_claude_json_stream,
    format_init,
    format_json_object,
    format_result,
    format_tool_result,
    format_tool_result_content,
    format_tool_use,
)


class TestLogFormatter:
    """Test cases for log formatter functions"""

    def test_format_claude_json_stream(self):
        """Test formatting complete JSON stream"""
        json_stream = "\n".join(
            [
                json.dumps(
                    {"type": "system", "subtype": "init", "cwd": "/home", "model": "claude-3"}
                ),
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {"content": [{"type": "text", "text": "Hello"}]},
                    }
                ),
                json.dumps(
                    {"type": "result", "result": "Done", "duration_ms": 1000, "cost_usd": 0.01}
                ),
            ]
        )

        result = format_claude_json_stream(json_stream)
        assert "Initializing: cwd=/home, model=claude-3" in result
        assert "Hello" in result
        assert "Done" in result
        assert "duration=1.0s" in result

    def test_format_claude_json_stream_with_invalid_json(self):
        """Test formatting stream with invalid JSON"""
        json_stream = "valid line\n{invalid json}\n"
        result = format_claude_json_stream(json_stream)
        assert "[Error parsing JSON]" in result
        assert "{invalid json}" in result

    def test_format_claude_json_stream_empty(self):
        """Test formatting empty stream"""
        result = format_claude_json_stream("")
        assert result == ""

    def test_format_json_object_unknown_type(self):
        """Test formatting unknown message type"""
        data = {"type": "unknown", "content": "test"}
        result = format_json_object(data)
        assert result == ""

    def test_format_init(self):
        """Test formatting init message"""
        data = {"cwd": "/Users/test", "model": "claude-3.5-sonnet"}
        result = format_init(data)
        assert result == "Initializing: cwd=/Users/test, model=claude-3.5-sonnet"

    def test_format_assistant_message_with_text(self):
        """Test formatting assistant message with text"""
        data = {
            "message": {
                "content": [
                    {"type": "text", "text": "First line"},
                    {"type": "text", "text": "Second line"},
                ]
            }
        }
        result = format_assistant_message(data)
        assert "First line" in result
        assert "Second line" in result

    def test_format_assistant_message_with_tool_use(self):
        """Test formatting assistant message with tool use"""
        data = {
            "message": {
                "content": [
                    {"type": "text", "text": "Running command:"},
                    {
                        "type": "tool_use",
                        "name": "Bash",
                        "input": {"command": "ls -la", "description": "List files"},
                    },
                ]
            }
        }
        result = format_assistant_message(data)
        assert "Running command:" in result
        assert '* Bash("ls -la")' in result
        assert "Description: List files" in result

    def test_format_assistant_message_empty(self):
        """Test formatting assistant message with no content"""
        data = {"message": {"content": []}}
        result = format_assistant_message(data)
        assert result == ""

    def test_format_tool_use_todo_write(self):
        """Test formatting TodoWrite tool use"""
        result = format_tool_use(
            "TodoWrite",
            {
                "todos": [
                    {"id": "1", "content": "Task 1", "status": "pending"},
                    {"id": "2", "content": "Task 2", "status": "completed"},
                ]
            },
        )
        assert "* TodoWrite(todos=2)" in result
        assert "[1] ☐ Task 1 (pending)" in result
        assert "[2] ✓ Task 2 (completed)" in result

    def test_format_tool_use_bash(self):
        """Test formatting Bash tool use"""
        result = format_tool_use(
            "Bash", {"command": "echo 'hello'", "description": "Print greeting"}
        )
        assert "* Bash(\"echo 'hello'\")" in result
        assert "Description: Print greeting" in result

    def test_format_tool_use_web_search(self):
        """Test formatting WebSearch tool use"""
        result = format_tool_use("WebSearch", {"query": "Python testing"})
        assert '* WebSearch("Python testing")' in result

    def test_format_tool_use_read(self):
        """Test formatting Read tool use"""
        result = format_tool_use("Read", {"file_path": "/path/to/file.py"})
        assert '* Read("/path/to/file.py")' in result

    def test_format_tool_use_edit(self):
        """Test formatting Edit tool use"""
        result = format_tool_use(
            "Edit",
            {
                "file_path": "/test.py",
                "old_string": "def old_function():\n    pass",
                "new_string": "def new_function():\n    return True",
            },
        )
        assert '* Edit("/test.py")' in result
        assert "Before: def old_function():\\n    pass..." in result
        assert "After: def new_function():\\n    return True..." in result

    def test_format_tool_use_multi_edit(self):
        """Test formatting MultiEdit tool use"""
        result = format_tool_use(
            "MultiEdit",
            {
                "file_path": "/test.py",
                "edits": [
                    {"old_string": "old1", "new_string": "new1"},
                    {"old_string": "old2", "new_string": "new2"},
                    {"old_string": "old3", "new_string": "new3"},
                    {"old_string": "old4", "new_string": "new4"},
                ],
            },
        )
        assert '* MultiEdit("/test.py")' in result
        assert "Edit 1: old1... → new1..." in result
        assert "Edit 3: old3... → new3..." in result
        assert "... and 1 more edits" in result

    def test_format_tool_use_unknown(self):
        """Test formatting unknown tool use"""
        result = format_tool_use(
            "UnknownTool",
            {"param1": "value1", "param2": "value2", "param3": "value3", "param4": "value4"},
        )
        assert "* UnknownTool(" in result
        assert "param1='value1'" in result
        assert "... (1 more)" in result

    def test_format_tool_result_with_results(self):
        """Test formatting tool result message"""
        data = {
            "message": {"content": [{"type": "tool_result", "content": "Operation successful"}]}
        }
        result = format_tool_result(data)
        assert "Tool result: Operation successful" in result

    def test_format_tool_result_empty(self):
        """Test formatting empty tool result"""
        data = {"message": {"content": []}}
        result = format_tool_result(data)
        assert result == ""

    def test_format_tool_result_content_git_status(self):
        """Test formatting git status result"""
        content = """On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
  modified:   file1.py
  modified:   file2.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
  new_file.py"""

        result = format_tool_result_content(content)
        assert "Tool result: On branch main" in result
        assert "Your branch is up to date" in result
        assert "modified:   file1.py" in result

    def test_format_tool_result_content_web_search(self):
        """Test formatting web search result"""
        content = """Web search results for: Python testing
Links: [https://example.com, https://test.com]
not show any relevant results"""

        result = format_tool_result_content(content)
        assert "Tool result: Web search results" in result
        assert "Search results retrieved" in result
        assert "No matching package found" in result

    def test_format_tool_result_content_ls(self):
        """Test formatting ls command result"""
        content = """- /Users/test/file1.py
- /Users/test/file2.py
- /Users/test/dir1/
- /Users/test/dir2/"""

        result = format_tool_result_content(content)
        assert "Tool result: Directory contents retrieved" in result
        assert "- /Users/test/file1.py" in result

    def test_format_tool_result_content_file_content(self):
        """Test formatting file content result"""
        content = """     1\t#!/usr/bin/env python3
     2\timport os
     3\timport sys
     4\t
     5\tdef main():
     6\t    print("Hello")"""

        result = format_tool_result_content(content)
        assert "Tool result: File content (6 lines)" in result
        assert "import os" in result
        assert "import sys" in result

    def test_format_tool_result_content_file_update(self):
        """Test formatting file update result"""
        content = """The file has been updated successfully.
Added new function
Updated imports"""

        result = format_tool_result_content(content)
        assert "Tool result: File updated successfully" in result
        assert "Added new function" in result
        assert "Updated imports" in result

    def test_format_tool_result_content_other(self):
        """Test formatting other tool results"""
        content = "Simple result"
        result = format_tool_result_content(content)
        assert result == "Tool result: Simple result"

    def test_format_tool_result_content_long_other(self):
        """Test formatting long other results"""
        lines = [f"Line {i}" for i in range(10)]
        content = "\n".join(lines)
        result = format_tool_result_content(content)
        assert "Tool result: Line 0" in result
        assert "Line 1" in result
        assert "Line 2" in result
        assert "... (7 more lines)" in result

    def test_format_result(self):
        """Test formatting final result"""
        data = {
            "result": "Task completed successfully",
            "duration_ms": 5500,
            "cost_usd": 0.025,
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 50,
            },
        }
        result = format_result(data)
        assert "Task completed successfully" in result
        assert "duration=5.5s" in result
        assert "cost=$0.025" in result
        assert "total_tokens=1,650" in result
