#!/usr/bin/env python3
"""Integration tests for xoncc formatters"""

import json
from io import StringIO
from unittest.mock import patch

from xoncc.claude_json_formatter import format_claude_json_stream as legacy_format
from xoncc.formatters import RealtimeClaudeFormatter, format_claude_json_stream
from xoncc.realtime_json_formatter import RealtimeClaudeFormatter as LegacyRealtimeFormatter


class TestFormatterIntegration:
    """Test formatter integration and backward compatibility"""

    def test_realtime_formatter_backward_compatibility(self):
        """Test that legacy module still works"""
        formatter1 = RealtimeClaudeFormatter()
        formatter2 = LegacyRealtimeFormatter()

        # Should be the same class
        assert type(formatter1) is type(formatter2)

    def test_log_formatter_backward_compatibility(self):
        """Test that legacy log formatter still works"""
        json_stream = json.dumps(
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Hello world"}]}}
        )

        # Test new formatter
        result1 = format_claude_json_stream(json_stream)

        # Test legacy formatter via stream
        stream = StringIO(json_stream)
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            legacy_format(stream)
            result2 = mock_stdout.getvalue()

        # Both should have formatted content
        assert "Hello world" in result1
        assert "Hello world" in result2

    def test_complete_claude_session(self):
        """Test formatting a complete Claude session"""
        json_lines = [
            json.dumps(
                {
                    "type": "system",
                    "subtype": "init",
                    "tools": ["Bash", "Read", "Write"],
                    "cwd": "/home/user",
                    "model": "claude-3.5-sonnet",
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "text",
                                "text": "I'll help you with that. Let me check the files.",
                            },
                            {
                                "type": "tool_use",
                                "name": "Read",
                                "input": {"file_path": "/home/user/test.py"},
                            },
                        ],
                        "usage": {"input_tokens": 100, "output_tokens": 50},
                    },
                }
            ),
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "content": [
                            {
                                "type": "tool_result",
                                "content": "def hello():\n    print('Hello, world!')",
                            }
                        ]
                    },
                }
            ),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "text",
                                "text": "I see you have a simple hello function. Let me run it.",
                            }
                        ]
                    },
                }
            ),
            json.dumps(
                {
                    "type": "result",
                    "result": "Task completed successfully",
                    "duration_ms": 3000,
                    "cost_usd": 0.005,
                    "usage": {
                        "input_tokens": 150,
                        "output_tokens": 75,
                        "cache_creation_input_tokens": 10,
                        "cache_read_input_tokens": 5,
                    },
                }
            ),
        ]

        # Test real-time formatter
        formatter = RealtimeClaudeFormatter()
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            formatter.format_stream(json_lines)
            realtime_output = mock_stdout.getvalue()

        assert "Available tools: Bash, Read, Write" in realtime_output
        assert "⏺ Read: /home/user/test.py" in realtime_output
        assert "I'll help you with that" in realtime_output
        assert "token: 240 cost: $0.01" in realtime_output

        # Test log formatter
        json_stream = "\n".join(json_lines)
        log_output = format_claude_json_stream(json_stream)

        assert "Initializing: cwd=/home/user, model=claude-3.5-sonnet" in log_output
        assert '* Read("/home/user/test.py")' in log_output
        assert "Task completed successfully" in log_output
        assert "duration=3.0s cost=$0.005 total_tokens=240" in log_output

    def test_streaming_content(self):
        """Test streaming content handling"""
        json_lines = [
            json.dumps({"type": "content_block_delta", "delta": {"text": "Hello"}}),
            json.dumps({"type": "content_block_delta", "delta": {"text": " world"}}),
            json.dumps({"type": "content_block_delta", "delta": {"text": "!"}}),
        ]

        formatter = RealtimeClaudeFormatter()
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            for line in json_lines:
                formatter.process_json_line(line)
            output = mock_stdout.getvalue()

        # Streaming content includes carriage returns
        assert "Hello" in output
        assert " world" in output
        assert "!" in output

    def test_tool_use_and_results(self):
        """Test tool use and result formatting"""
        json_lines = [
            json.dumps(
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": "ls -la", "description": "List all files"},
                }
            ),
            json.dumps({"type": "tool_result", "content": "file1.txt\nfile2.py\nfile3.md"}),
            json.dumps({"type": "tool_result", "is_error": True, "content": "Permission denied"}),
        ]

        formatter = RealtimeClaudeFormatter()
        outputs = []

        for line in json_lines:
            data = json.loads(line)
            content = formatter.extract_content_from_json(data)
            if content:
                outputs.append(content)

        assert "⏺ Bash: List all files\n" in outputs
        assert any("file1.txt" in o for o in outputs)
        assert any("Error: Permission denied" in o for o in outputs)

    def test_thinking_blocks(self):
        """Test thinking block formatting"""
        data = {"type": "thinking", "content": "I need to analyze this code to find the bug..."}

        formatter = RealtimeClaudeFormatter()
        # format_thinking is accessed through tool_formatter
        result = formatter.tool_formatter.format_thinking(data)

        assert result == "💭 I need to analyze this code to find the bug...\n"

    def test_cost_calculation(self):
        """Test token and cost calculation"""
        formatter = RealtimeClaudeFormatter()

        # Test with assistant message
        data = {
            "type": "assistant",
            "message": {
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "cache_creation_input_tokens": 100,
                    "cache_read_input_tokens": 50,
                }
            },
        }

        formatter.extract_usage_info(data)
        assert formatter.total_tokens == 1650
        expected_cost = 1000 * 3.0 / 1000000 + 500 * 15.0 / 1000000
        assert abs(formatter.cost - expected_cost) < 0.0001

        # Test with result type (overrides calculation)
        data = {
            "type": "result",
            "cost_usd": 0.025,
            "usage": {"input_tokens": 2000, "output_tokens": 1000},
        }

        formatter.extract_usage_info(data)
        assert formatter.cost == 0.025  # Should use provided cost
        assert formatter.total_tokens == 3000
