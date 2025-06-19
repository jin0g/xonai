"""Test subprocess handling to ensure no deadlocks."""

import json
import time
from unittest.mock import Mock, patch

from xonai.ai.base import ErrorResponse, InitResponse, MessageResponse
from xonai.ai.claude import ClaudeAI


class TestSubprocessHandling:
    """Test subprocess handling in ClaudeAI."""

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_no_deadlock_with_large_stderr(self, mock_which, mock_popen):
        """Test that large stderr output doesn't cause deadlock."""
        mock_which.return_value = "/usr/bin/claude"

        # Create mock process
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Simulate large stdout output (multiple JSON lines)
        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "123"}),
            json.dumps({"type": "content_block_delta", "delta": {"text": "Hello"}}),
            json.dumps({"type": "content_block_delta", "delta": {"text": " world"}}),
            json.dumps({"type": "result", "usage": {"input_tokens": 10, "output_tokens": 20}}),
        ]

        # Simulate large stderr output that could cause deadlock
        stderr_lines = ["Error line " + str(i) + "\n" for i in range(1000)]

        # Mock stdout as an iterator
        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])

        # Mock stderr to simulate blocking behavior
        class MockStderr:
            def __init__(self, lines):
                self.lines = lines
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index < len(self.lines):
                    line = self.lines[self.index]
                    self.index += 1
                    time.sleep(0.001)  # Simulate slow stderr
                    return line
                raise StopIteration

        mock_proc.stderr = MockStderr(stderr_lines)
        mock_proc.wait.return_value = 1  # Non-zero exit

        # Run ClaudeAI
        ai = ClaudeAI()
        responses = list(ai("test query"))

        # Should complete without hanging
        assert len(responses) > 0

        # Should have processed stdout correctly
        init_responses = [r for r in responses if isinstance(r, InitResponse)]
        assert len(init_responses) == 1

        message_responses = [r for r in responses if isinstance(r, MessageResponse)]
        assert len(message_responses) == 2
        assert "".join(r.content for r in message_responses) == "Hello world"

        # Should have captured stderr error
        error_responses = [r for r in responses if isinstance(r, ErrorResponse)]
        assert len(error_responses) == 1
        assert "Error line" in error_responses[0].content

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_keyboard_interrupt_cleanup(self, mock_which, mock_popen):
        """Test that KeyboardInterrupt properly cleans up threads."""
        mock_which.return_value = "/usr/bin/claude"

        # Create mock process
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Mock stdout to raise KeyboardInterrupt after first line
        def stdout_generator():
            yield json.dumps({"type": "system", "subtype": "init"}) + "\n"
            raise KeyboardInterrupt()

        mock_proc.stdout = stdout_generator()
        mock_proc.stderr = iter([])  # Empty stderr
        mock_proc.terminate = Mock()
        mock_proc.wait = Mock()

        # Run ClaudeAI
        ai = ClaudeAI()
        responses = list(ai("test query"))

        # Should handle interrupt gracefully
        assert mock_proc.terminate.called

        # Should return interrupt error
        error_responses = [r for r in responses if isinstance(r, ErrorResponse)]
        assert len(error_responses) == 1
        assert "Interrupted" in error_responses[0].content

    @patch("xonai.ai.claude.subprocess.Popen")
    @patch("xonai.ai.claude.shutil.which")
    def test_json_parsing_with_invalid_lines(self, mock_which, mock_popen):
        """Test that invalid JSON lines are skipped without breaking the stream."""
        mock_which.return_value = "/usr/bin/claude"

        # Create mock process
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Mix valid and invalid JSON
        stdout_lines = [
            json.dumps({"type": "system", "subtype": "init"}),
            "Invalid JSON line",
            json.dumps({"type": "content_block_delta", "delta": {"text": "Hello"}}),
            "{broken json",
            json.dumps({"type": "result", "usage": {"input_tokens": 10, "output_tokens": 20}}),
        ]

        mock_proc.stdout = iter([line + "\n" for line in stdout_lines])
        mock_proc.stderr = iter([])
        mock_proc.wait.return_value = 0

        # Run ClaudeAI
        ai = ClaudeAI()
        responses = list(ai("test query"))

        # Should skip invalid lines and process valid ones
        assert len(responses) >= 3  # init, message, result

        # Check that valid responses were processed
        init_responses = [r for r in responses if isinstance(r, InitResponse)]
        assert len(init_responses) == 1

        message_responses = [r for r in responses if isinstance(r, MessageResponse)]
        assert any("Hello" in r.content for r in message_responses)
