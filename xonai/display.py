"""Display formatting for AI responses with emoji-based indicators."""

import shutil
from typing import Optional

from rich.console import Console
from rich.text import Text

from .ai import (
    ErrorResponse,
    InitResponse,
    MessageResponse,
    Response,
    ResultResponse,
    ToolResultResponse,
    ToolUseResponse,
)


class ResponseFormatter:
    """Format and display AI responses with rich formatting."""

    def __init__(self):
        """Initialize the formatter."""
        self.console = Console(force_terminal=True, legacy_windows=False)
        self._current_tool = None
        self._last_was_newline = True

    def format(self, response: Response) -> None:
        """
        Format and print an AI response.

        Args:
            response: The Response to format and display
        """
        output = self._format_response(response)
        if output:
            if isinstance(response, MessageResponse):
                # Streaming text - print without newline
                print(output, end="", flush=True)
                self._last_was_newline = output.endswith("\n")
            else:
                # Other types - print with newline if needed
                if not self._last_was_newline:
                    print()  # Add newline after streaming text
                print(output)
                self._last_was_newline = True

    def _format_response(self, response: Response) -> str:
        """Format a response based on its type."""
        if isinstance(response, InitResponse):
            return self._format_init(response)
        elif isinstance(response, MessageResponse):
            return response.content  # Direct streaming output
        elif isinstance(response, ToolUseResponse):
            return self._format_tool_use(response)
        elif isinstance(response, ToolResultResponse):
            return self._format_tool_result(response)
        elif isinstance(response, ErrorResponse):
            return self._format_error(response)
        elif isinstance(response, ResultResponse):
            return self._format_result(response)
        return ""

    def _format_init(self, response: InitResponse) -> str:
        """Format initialization message."""
        # Default content for Claude Code
        ai_name = response.content or "Claude Code"
        model = response.model or "unknown"
        session_id = response.session_id or ""

        if session_id:
            return f"🚀 {ai_name}: model={model}, id={session_id}"
        else:
            return f"🚀 {ai_name}: model={model}"

    def _format_tool_use(self, response: ToolUseResponse) -> str:
        """Format tool usage with appropriate emoji."""
        tool_name = response.tool
        self._current_tool = tool_name
        content = response.content

        # Map tool names to emojis and format content
        if tool_name == "LS":
            return self._truncate_to_width(f"📁 {content}")
        elif tool_name in ["Read", "NotebookRead"]:
            return self._truncate_to_width(f"📖 {content}")
        elif tool_name in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
            return self._truncate_to_width(f"✏️ {content}")
        elif tool_name == "Bash":
            return self._truncate_to_width(f"🔧 {content}")
        elif tool_name == "WebSearch":
            return self._truncate_to_width(f"🔍 {content}")
        elif tool_name == "WebFetch":
            return self._truncate_to_width(f"🌐 {content}")
        elif tool_name == "TodoRead":
            return "📋 TodoRead"
        elif tool_name == "TodoWrite":
            # Parse todos from content if it's a special format
            return "📝 TodoWrite"
        elif tool_name == "Task":
            return self._truncate_to_width(f"🤖 Task: {content}")
        elif tool_name in ["Glob", "Grep"]:
            return self._truncate_to_width(f"🔍 {content}")
        else:
            # Generic tool format
            return self._truncate_to_width(f"🔧 {tool_name}: {content}")


    def _format_tool_result(self, response: ToolResultResponse) -> str:
        """Format tool results - show all content."""
        content = response.content
        tool = response.tool

        if not content.strip():
            return "(empty output)"

        # Show tool name with content
        if tool:
            return f"[{tool}] {content}"
        else:
            return content

    def _format_error(self, response: ErrorResponse) -> str:
        """Format error messages."""
        # Error messages are not truncated, with blank line before
        return f"\n❌ {response.content}"

    def _format_result(self, response: ResultResponse) -> str:
        """Format final result summary."""
        # Content already contains formatted stats
        stats = response.content
        token_count = response.token

        if stats:
            return f"\n📊 {stats}, next_session_tokens={token_count:,}"
        else:
            return f"\n📊 next_session_tokens={token_count:,}"

    def _truncate_to_width(self, text: str, width: Optional[int] = None) -> str:
        """Truncate text to fit terminal width using Rich."""
        if width is None:
            columns, _ = shutil.get_terminal_size(fallback=(80, 24))
            width = columns

        lines = text.split("\n")
        result = []

        for _, line in enumerate(lines[:5]):  # Max 5 lines
            # Create a Text object from the line (preserving ANSI codes)
            text_obj = Text.from_ansi(line)

            # Check if truncation is needed
            if self.console.measure(text_obj).maximum > width - 3:
                # Manually truncate to ensure we get exactly width-3 characters
                plain_text = text_obj.plain
                truncated = ""
                current_width = 0

                for char in plain_text:
                    char_text = Text(char)
                    char_width = self.console.measure(char_text).maximum
                    if current_width + char_width > width - 3:
                        break
                    truncated += char
                    current_width += char_width

                result.append(truncated + "...")
            else:
                result.append(line)

        if len(lines) > 5:
            result.append("...")

        return "\n".join(result)
