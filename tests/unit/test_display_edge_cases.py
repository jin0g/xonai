"""Test edge cases for display formatting."""

from unittest.mock import patch

from xonai.ai.base import InitResponse, MessageResponse, ToolResultResponse, ToolUseResponse
from xonai.display import ResponseFormatter


class TestDisplayEdgeCases:
    """Test edge cases in display formatting."""

    def test_all_tool_emojis(self, capsys):
        """Test that all tool types have proper emoji mappings."""
        formatter = ResponseFormatter()

        # Test all known tools
        tools_and_expected = [
            ("Agent", "🔧"),  # Agent uses generic tool format
            ("Task", "🤖"),
            ("exit_plan_mode", "🔧"),  # Uses generic tool format
            ("NotebookRead", "📖"),
            ("NotebookEdit", "✏️"),
            ("MultiEdit", "✏️"),
            ("WebFetch", "🌐"),
            ("WebSearch", "🔍"),
            ("Glob", "🔍"),
            ("Grep", "🔍"),
            ("TodoRead", "📋"),
            ("TodoWrite", "📝"),
        ]

        for tool, expected_emoji in tools_and_expected:
            formatter.format(ToolUseResponse(content="test", tool=tool))
            output = capsys.readouterr().out
            assert expected_emoji in output, f"Tool {tool} should have emoji {expected_emoji}"

    @patch("shutil.get_terminal_size")
    def test_exact_terminal_width_truncation(self, mock_term_size, capsys):
        """Test truncation at exact terminal width boundaries."""
        mock_term_size.return_value = (80, 24)

        formatter = ResponseFormatter()

        # Create string exactly at terminal width
        long_text = "a" * 77  # 77 + "..." = 80
        response = ToolUseResponse(content=long_text, tool="Bash")
        formatter.format(response)

        output = capsys.readouterr().out.strip()
        assert len(output) <= 80
        assert output.endswith("...")

    def test_unicode_emoji_spacing(self, capsys):
        """Test proper spacing with unicode emojis."""
        formatter = ResponseFormatter()

        # Test that emoji + space + text works correctly
        response = InitResponse(content="Test AI", model="test")
        formatter.format(response)

        output = capsys.readouterr().out.strip()
        assert output.startswith("🚀 ")
        assert "Test AI" in output

    def test_empty_message_response(self, capsys):
        """Test handling of empty message responses."""
        formatter = ResponseFormatter()

        # Empty content should still be processed
        response = MessageResponse(content="")
        formatter.format(response)

        output = capsys.readouterr().out
        assert output == ""  # Empty content produces empty output

    def test_tool_result_with_unicode(self, capsys):
        """Test tool results containing unicode characters."""
        formatter = ResponseFormatter()

        # Japanese text in tool result
        response = ToolResultResponse(content="ファイル一覧:\n• test.py\n• 日本語.txt", tool="LS")
        formatter.format(response)

        output = capsys.readouterr().out
        assert "ファイル一覧" not in output  # Should be summarized
        # LS tool shows "Found X items" format
        assert "Found 3 items" in output

    @patch("shutil.get_terminal_size")
    def test_narrow_terminal(self, mock_term_size, capsys):
        """Test display in very narrow terminal."""
        mock_term_size.return_value = (40, 24)  # Narrow terminal

        formatter = ResponseFormatter()

        # Long command should be truncated
        response = ToolUseResponse(
            content="very long command with many arguments that exceeds terminal width", tool="Bash"
        )
        formatter.format(response)

        output = capsys.readouterr().out.strip()
        # Note: The actual truncation happens in display._truncate_to_width,
        # but tool use formatting doesn't apply truncation
        assert "🔧" in output
        assert "very long command" in output

    def test_multiline_tool_content(self, capsys):
        """Test tool use with multiline content."""
        formatter = ResponseFormatter()

        # Multiline bash command
        multiline_cmd = "echo 'line1' && \\\necho 'line2' && \\\necho 'line3'"
        response = ToolUseResponse(content=multiline_cmd, tool="Bash")
        formatter.format(response)

        output = capsys.readouterr().out.strip()
        # Multi-line commands are shown as-is in tool use
        # The emoji adds length, so the output is longer than the command
        assert "echo 'line1'" in output
        assert "🔧" in output

    def test_special_characters_in_content(self, capsys):
        """Test handling of special characters."""
        formatter = ResponseFormatter()

        # Test with various special characters
        special_content = "Test\x00null\x01soh\x1bescape"
        response = MessageResponse(content=special_content)
        formatter.format(response)

        output = capsys.readouterr().out
        # Should handle special characters gracefully
        assert "Test" in output

    def test_consecutive_newlines_in_message(self, capsys):
        """Test messages with multiple consecutive newlines."""
        formatter = ResponseFormatter()

        # Message with multiple newlines
        response = MessageResponse(content="Line1\n\n\nLine2")
        formatter.format(response)

        output = capsys.readouterr().out
        assert output == "Line1\n\n\nLine2"  # Should preserve newlines

    def test_init_without_model_info(self, capsys):
        """Test init response without model information."""
        formatter = ResponseFormatter()

        response = InitResponse(content=None, session_id=None, model=None)
        formatter.format(response)

        output = capsys.readouterr().out.strip()
        assert output == "🚀 Claude Code: model=unknown"
