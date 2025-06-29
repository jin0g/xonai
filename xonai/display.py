"""Display formatting for AI responses with emoji-based indicators."""

import shutil
from typing import Optional

from rich.console import Console
from rich.text import Text

from .agents import (
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
            elif isinstance(response, InitResponse):
                # Init on new line if needed
                if not self._last_was_newline:
                    print()
                print(output)
                self._last_was_newline = True
            elif isinstance(response, ResultResponse):
                # Result gets a blank line before
                if not self._last_was_newline:
                    print()
                print()  # Blank line before result
                print(output)
                self._last_was_newline = True
            else:
                # Tool use/results - simple output, no extra spacing
                if not self._last_was_newline:
                    print()  # Complete any pending line
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
        agent_name = response.content or "Claude Code"
        model = response.model or "unknown"
        session_id = response.session_id or ""

        if session_id:
            return f"🚀 {agent_name}: model={model}, id={session_id}"
        else:
            return f"🚀 {agent_name}: model={model}"

    def _format_tool_use(self, response: ToolUseResponse) -> str:
        """Format tool usage with appropriate emoji."""
        tool_name = response.tool
        self._current_tool = tool_name
        content = response.content

        # Map tool names to emojis and simplified content
        if tool_name == "LS":
            # Just show the path being listed
            return f"📁 ls {content}"
        elif tool_name in ["Read", "NotebookRead"]:
            # Just show filename
            return f"📖 Reading {content}"
        elif tool_name in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
            # Just show filename
            return f"✏️ Editing {content}"
        elif tool_name == "Bash":
            # Show command but truncate if too long
            if len(content) > 60:
                return f"🔧 {content[:57]}..."
            return f"🔧 {content}"
        elif tool_name == "WebSearch":
            return f"🔍 Searching: {content}"
        elif tool_name == "WebFetch":
            return f"🌐 Fetching: {content}"
        elif tool_name == "TodoRead":
            return "📋 Reading todos"
        elif tool_name == "TodoWrite":
            return "📝 Updating todos"
        elif tool_name == "Task":
            return f"🤖 Task: {content}"
        elif tool_name in ["Glob", "Grep"]:
            # Show pattern only
            if " in " in content:
                pattern = content.split(" in ")[0]
                return f"🔍 Searching for: {pattern}"
            return f"🔍 Searching: {content}"
        else:
            # Generic tool format
            return f"🔧 {tool_name}: {content}"

    def _format_tool_result(self, response: ToolResultResponse) -> str:
        """Format tool results - simplified output."""
        content = response.content
        tool = response.tool

        if not content or not content.strip():
            return ""  # Don't show empty results

        # Simplify output based on tool
        if tool == "Read":
            line_count = content.count("\n") + 1
            return f"  → Read {line_count} lines"
        elif tool == "LS":
            # Count files/directories
            items = content.strip().split("\n")
            return f"  → Found {len(items)} items"
        elif tool in ["Edit", "MultiEdit"]:
            # Show edit summary
            return "  → File updated"
        elif tool == "Write":
            return "  → File written"
        elif tool == "Bash":
            # Show first line of output if short, otherwise just indicate output
            lines = content.strip().split("\n")
            if len(lines) == 1 and len(lines[0]) < 60:
                return f"  → {lines[0]}"
            elif len(lines) > 1:
                return f"  → Output: {len(lines)} lines"
            else:
                return "  → Command completed"
        elif tool in ["Glob", "Grep"]:
            # Count matches
            matches = content.strip().split("\n") if content.strip() else []
            if matches:
                return f"  → Found {len(matches)} matches"
            else:
                return "  → No matches found"
        elif tool == "TodoRead":
            # Count todos
            import json

            try:
                todos = json.loads(content)
                return f"  → {len(todos)} todos"
            except Exception:
                return "  → Todos listed"
        elif tool == "TodoWrite":
            return "  → Todos updated"
        else:
            # For other tools, show brief summary
            lines = content.strip().split("\n")
            if len(lines) == 1 and len(lines[0]) < 80:
                return f"  → {lines[0]}"
            else:
                return "  → Completed"

    def _format_error(self, response: ErrorResponse) -> str:
        """Format error messages."""
        # Don't show errors to the user - just return empty
        return ""

    def _format_result(self, response: ResultResponse) -> str:
        """Format final result summary."""
        # Content already contains formatted stats
        stats = response.content
        token_count = response.token

        if stats:
            return f"📊 {stats}, next_session_tokens={token_count}"
        else:
            return f"📊 next_session_tokens={token_count}"

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
