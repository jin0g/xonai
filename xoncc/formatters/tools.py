#!/usr/bin/env python3
"""Tool formatting utilities for Claude output"""

from typing import Any, Dict, Optional


class ToolFormatter:
    """Formatter for tool use and tool result messages"""

    @staticmethod
    def format_tool_use(data: Dict[str, Any]) -> Optional[str]:
        """Format tool use information"""
        if data.get("type") != "tool_use":
            return None

        tool_name = data.get("name", "Unknown Tool")
        input_data = data.get("input", {})

        if tool_name == "TodoRead" and not input_data:
            # Special case for TodoRead with no input
            return f"⏺ {tool_name}\n"

        description = ToolFormatter._get_tool_description(tool_name, input_data)
        return f"⏺ {tool_name}{description}\n"

    @staticmethod
    def _get_tool_description(tool_name: str, input_data: Dict[str, Any]) -> str:
        """Extract relevant description based on tool type"""
        if "description" in input_data:
            return f": {input_data['description']}"

        elif tool_name == "Task" and "prompt" in input_data:
            return f": {input_data.get('description', 'Task')}"

        elif "query" in input_data:
            return f": {input_data['query']}"

        elif tool_name == "Bash" and "command" in input_data:
            desc = input_data.get("description", "")
            if desc:
                return f": {desc}"
            else:
                cmd = input_data["command"]
                return f": {cmd[:50]}..." if len(cmd) > 50 else f": {cmd}"

        elif "file_path" in input_data:
            return f": {input_data['file_path']}"

        elif "pattern" in input_data:
            return f": {input_data['pattern']}"

        elif tool_name == "TodoWrite" and "todos" in input_data:
            count = len(input_data["todos"])
            return f": {count} todo{'s' if count != 1 else ''}"

        return ""

    @staticmethod
    def format_tool_result(data: Dict[str, Any]) -> Optional[str]:
        """Format tool result information"""
        if data.get("type") != "tool_result":
            return None

        is_error = data.get("is_error", False)
        content = data.get("content", "")

        if is_error:
            return f"  ⎿ Error: {content}\n"
        elif isinstance(content, str) and content.strip():
            # Truncate very long results
            if len(content) > 200:
                content = content[:197] + "..."
            return f"  ⎿ {content}\n"

        return None

    @staticmethod
    def format_thinking(data: Dict[str, Any]) -> Optional[str]:
        """Format thinking blocks"""
        if data.get("type") != "thinking":
            return None

        thinking_text = data.get("content", "")
        if thinking_text.strip():
            # Show thinking in a subtle way
            if len(thinking_text) > 100:
                thinking_text = thinking_text[:100] + "..."
            return f"💭 {thinking_text}\n"

        return None
