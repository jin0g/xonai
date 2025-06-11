#!/usr/bin/env python3
"""Tests for real-time formatter"""

import json

from xoncc.formatters.realtime import RealtimeClaudeFormatter


class TestRealtimeClaudeFormatter:
    """Test cases for RealtimeClaudeFormatter"""

    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = RealtimeClaudeFormatter()

    def test_init(self):
        """Test formatter initialization"""
        assert self.formatter.total_tokens == 0
        assert self.formatter.cost == 0.0
        assert self.formatter.session_id is None
        assert self.formatter.is_streaming is False
        assert self.formatter.final_result_received is False

    def test_clear_current_line(self, capsys):
        """Test clearing current line"""
        self.formatter.clear_current_line()
        captured = capsys.readouterr()
        assert captured.out == "\r"
        assert self.formatter.last_line_length == 0

    def test_update_token_display(self, capsys):
        """Test token display update"""
        self.formatter.update_token_display(100)
        captured = capsys.readouterr()
        assert captured.out == " token: 100...\r"
        assert self.formatter.last_line_length == len(" token: 100...")

    def test_extract_usage_info_result_type(self):
        """Test extracting usage info from result type"""
        data = {
            "type": "result",
            "cost_usd": 0.05,
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 50,
            },
            "session_id": "test-session",
        }
        self.formatter.extract_usage_info(data)
        assert self.formatter.cost == 0.05
        assert self.formatter.total_tokens == 1650
        assert self.formatter.session_id == "test-session"

    def test_extract_usage_info_assistant_type(self):
        """Test extracting usage info from assistant type"""
        data = {
            "type": "assistant",
            "message": {"usage": {"input_tokens": 1000, "output_tokens": 500}},
        }
        self.formatter.extract_usage_info(data)
        expected_cost = 1000 * 3.0 / 1000000 + 500 * 15.0 / 1000000
        assert abs(self.formatter.cost - expected_cost) < 0.0001
        assert self.formatter.total_tokens == 1500

    def test_extract_content_from_json_result_type(self):
        """Test skipping result type content"""
        data = {"type": "result"}
        result = self.formatter.extract_content_from_json(data)
        assert result is None
        assert self.formatter.final_result_received is True

    def test_extract_content_from_json_system_init(self):
        """Test extracting system init content"""
        data = {"type": "system", "subtype": "init", "tools": ["Bash", "Read", "Write"]}
        result = self.formatter.extract_content_from_json(data)
        assert result == "🛠️  Available tools: Bash, Read, Write\n"

    def test_extract_content_from_json_tool_use(self):
        """Test extracting tool use content"""
        data = {
            "type": "tool_use",
            "name": "Bash",
            "input": {"command": "ls", "description": "List files"},
        }
        result = self.formatter.extract_content_from_json(data)
        assert result == "⏺ Bash: List files\n"

    def test_extract_content_from_json_assistant_message(self):
        """Test extracting assistant message content"""
        data = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Hello, world!"},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}},
                ]
            },
        }
        result = self.formatter.extract_content_from_json(data)
        assert "Hello, world!" in result
        assert "⏺ Read: /test.py" in result

    def test_extract_content_from_json_content_delta(self):
        """Test extracting streaming content delta"""
        data = {"type": "content_block_delta", "delta": {"text": "Streaming text"}}
        result = self.formatter.extract_content_from_json(data)
        assert result == "Streaming text"
        assert self.formatter.is_streaming is True

    def test_extract_content_from_json_content_block_start(self):
        """Test extracting content block start"""
        data = {
            "type": "content_block_start",
            "content_block": {"type": "text", "text": "Starting text"},
        }
        result = self.formatter.extract_content_from_json(data)
        assert result == "Starting text"

    def test_extract_content_from_json_progress(self):
        """Test extracting progress message"""
        data = {"type": "progress", "message": "Processing request"}
        result = self.formatter.extract_content_from_json(data)
        assert result == "⏳ Processing request\n"

    def test_extract_content_from_json_status(self):
        """Test extracting status message"""
        data = {"type": "status", "status": "Analyzing code"}
        result = self.formatter.extract_content_from_json(data)
        assert result == "📊 Analyzing code\n"

    def test_process_json_line_valid_json(self, capsys):
        """Test processing valid JSON line"""
        line = json.dumps(
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Test"}]}}
        )
        result = self.formatter.process_json_line(line)
        assert result is True
        captured = capsys.readouterr()
        assert "Test" in captured.out

    def test_process_json_line_invalid_json(self, capsys):
        """Test processing invalid JSON line"""
        line = "This is not JSON"
        result = self.formatter.process_json_line(line)
        assert result is True
        captured = capsys.readouterr()
        assert line in captured.out

    def test_process_json_line_empty(self):
        """Test processing empty line"""
        result = self.formatter.process_json_line("")
        assert result is False

    def test_process_json_line_with_streaming_tokens(self, capsys):
        """Test processing line with streaming and token display"""
        self.formatter.is_streaming = True
        self.formatter.total_tokens = 100
        line = json.dumps({"type": "content_block_delta", "delta": {"text": "Test"}})
        result = self.formatter.process_json_line(line)
        assert result is True
        captured = capsys.readouterr()
        assert "Test" in captured.out
        assert "token: 100..." in captured.out

    def test_finalize_output_with_tokens(self, capsys):
        """Test finalizing output with tokens and cost"""
        self.formatter.total_tokens = 1000
        self.formatter.cost = 0.0123
        self.formatter.finalize_output()
        captured = capsys.readouterr()
        assert "token: 1000 cost: $0.01" in captured.out

    def test_finalize_output_with_active_display(self, capsys):
        """Test finalizing output with active token display"""
        self.formatter.last_line_length = 10
        self.formatter.total_tokens = 500
        self.formatter.cost = 0.005
        self.formatter.finalize_output()
        captured = capsys.readouterr()
        output_lines = captured.out.split("\n")
        assert len(output_lines) >= 2
        assert "token: 500 cost: $0.01" in captured.out

    def test_format_stream(self, capsys):
        """Test formatting complete stream"""
        stream = [
            json.dumps({"type": "system", "subtype": "init", "tools": ["Bash"]}),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [{"type": "text", "text": "Hello"}],
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                    },
                }
            ),
            json.dumps({"type": "result", "cost_usd": 0.001}),
        ]

        self.formatter.format_stream(stream)
        captured = capsys.readouterr()
        assert "Available tools: Bash" in captured.out
        assert "Hello" in captured.out
        assert "token: 15" in captured.out
        assert "cost: $0.00" in captured.out

    def test_format_stream_with_exception(self, capsys):
        """Test format stream with exception handling"""

        def bad_stream():
            yield "good line"
            raise Exception("Stream error")

        self.formatter.format_stream(bad_stream())
        captured = capsys.readouterr()
        assert "good line" in captured.out
        assert "Error processing stream: Stream error" in captured.err

    def test_extract_direct_content_string(self):
        """Test extracting direct content from string"""
        result = self.formatter._extract_direct_content("Simple string")
        assert result == "Simple string"

    def test_extract_direct_content_list_with_text(self):
        """Test extracting direct content from list with text items"""
        content = [{"text": "First part"}, {"text": "Second part"}]
        result = self.formatter._extract_direct_content(content)
        assert result == "First part"

    def test_extract_direct_content_list_with_tool_use(self):
        """Test extracting direct content from list with tool use"""
        content = [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]
        result = self.formatter._extract_direct_content(content)
        assert "⏺ Bash: ls" in result

    def test_extract_direct_content_none(self):
        """Test extracting direct content returns None for invalid input"""
        assert self.formatter._extract_direct_content({}) is None
        assert self.formatter._extract_direct_content([]) is None
        assert self.formatter._extract_direct_content(None) is None
