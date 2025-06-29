"""Test xonai handling of complex queries that might cause deadlock."""

import json
from unittest.mock import Mock, patch

from xonai.ai.claude import ClaudeAI


class TestXonaiDeadlock:
    """Test xonai doesn't deadlock on complex queries."""

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_japanese_project_overview_query(self, mock_which, mock_popen):
        """Test the specific Japanese query that was causing issues."""
        mock_which.return_value = "/usr/bin/claude"

        # Create mock process
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Simulate Claude's typical response for project overview
        # This would normally be VERY long with many tool uses
        # Create JSON responses (split long lines for readability)
        init_data = {
            "type": "system",
            "subtype": "init",
            "session_id": "test-123",
            "model": "claude-3"
        }
        content_data = {
            "type": "content_block_delta",
            "delta": {"text": "プロジェクトの概要を把握します。\n"}
        }
        ls_tool = {
            "type": "assistant",
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "LS",
                    "input": {"path": "/"}
                }]
            }
        }
        ls_result = {
            "type": "user",
            "message": {
                "content": [{
                    "type": "tool_result",
                    "content": "file1.py\nfile2.py\nREADME.md"
                }]
            }
        }
        read_tool = {
            "type": "assistant",
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "Read",
                    "input": {"file_path": "README.md"}
                }]
            }
        }
        read_result = {
            "type": "user",
            "message": {
                "content": [{
                    "type": "tool_result",
                    "content": "# Project Title\n" * 100
                }]
            }
        }
        grep_tool = {
            "type": "assistant",
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "Grep",
                    "input": {"pattern": "class", "path": "."}
                }]
            }
        }
        grep_result_content = "\n".join([
            f"file{i}.py: class Example{i}" for i in range(50)
        ])
        grep_result = {
            "type": "user",
            "message": {
                "content": [{
                    "type": "tool_result",
                    "content": grep_result_content
                }]
            }
        }
        text1 = {"type": "content_block_delta", "delta": {"text": "このプロジェクトは..."}}
        text2 = {"type": "content_block_delta", "delta": {"text": "Pythonで書かれた..."}}
        result_data = {
            "type": "result",
            "usage": {"input_tokens": 5000, "output_tokens": 2000},
            "duration_ms": 5000,
            "cost_usd": 0.05
        }

        stdout_lines = [
            json.dumps(init_data),
            json.dumps(content_data),
            json.dumps(ls_tool),
            json.dumps(ls_result),
            json.dumps(read_tool),
            json.dumps(read_result),
            json.dumps(grep_tool),
            json.dumps(grep_result),
            json.dumps(text1),
            json.dumps(text2),
            json.dumps(result_data),
        ]

        # Simulate stderr output (warnings, debug info, etc.)
        stderr_content = "\n".join([
            "Warning: Large context size",
            "Debug: Processing file analysis",
            "Info: Using model claude-3",
        ] * 10)  # Repeat to simulate verbose output

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter(stderr_content.split("\n"))
        mock_proc.wait.return_value = 0

        # Run the query
        ai = ClaudeAI()
        query = "このプロジェクトの概要を把握して下さい"
        responses = list(ai(query))

        # Should complete without deadlock
        assert len(responses) > 0

        # Verify proper handling
        init_found = any(r.content == "Claude Code" for r in responses if hasattr(r, 'content'))
        assert init_found, "Should have init response"

        # Should have tool uses
        tool_uses = [r for r in responses if hasattr(r, 'tool')]
        assert len(tool_uses) > 0, "Should have tool uses"

        # Should have final result
        result_found = any(hasattr(r, 'token') for r in responses)
        assert result_found, "Should have result with token count"

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_simulate_actual_deadlock_scenario(self, mock_which, mock_popen):
        """Simulate the exact deadlock scenario with blocking stderr."""
        mock_which.return_value = "/usr/bin/claude"

        # Create mock process
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Create a custom stderr that would block if read sequentially
        class BlockingStderr:
            def __init__(self):
                self.data = ["Error: " + "x" * 8192 + "\n"] * 10  # Large stderr data
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index < len(self.data):
                    result = self.data[self.index]
                    self.index += 1
                    return result
                raise StopIteration

        # Stdout with lots of data
        stdout_data = []
        for i in range(100):
            stdout_data.append(json.dumps({
                "type": "content_block_delta",
                "delta": {"text": f"Processing item {i}...\n"}
            }))
        stdout_data.append(json.dumps({
            "type": "result",
            "usage": {"input_tokens": 1000, "output_tokens": 500}
        }))

        mock_proc.stdout = iter([line + "\n" for line in stdout_data])
        mock_proc.stderr = BlockingStderr()
        mock_proc.wait.return_value = 1  # Error exit

        # This should NOT deadlock with our fix
        ai = ClaudeAI()
        responses = list(ai("complex query"))

        # Should have processed all stdout
        message_count = sum(
            1 for r in responses
            if hasattr(r, 'content') and "Processing item" in str(r.content)
        )
        assert message_count == 100, f"Should have all 100 messages, got {message_count}"

        # Should have captured stderr error
        errors = [r for r in responses if r.__class__.__name__ == "ErrorResponse"]
        assert len(errors) > 0, "Should have error from stderr"
        assert "Error:" in errors[0].content

