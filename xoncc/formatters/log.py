#!/usr/bin/env python3
"""Claude CLI log JSON formatter for human-readable output"""

import json
import re
from typing import Any, Dict


def format_claude_json_stream(json_stream: str) -> str:
    """
    Convert Claude CLI JSON output to natural language format

    Args:
        json_stream: Newline-delimited JSON string

    Returns:
        Formatted output string
    """
    lines = json_stream.strip().split("\n")
    output_lines = []

    for line in lines:
        if not line.strip():
            continue

        try:
            data = json.loads(line)
            formatted = format_json_object(data)
            if formatted:
                output_lines.append(formatted)
        except json.JSONDecodeError:
            # Output unparseable lines as-is
            output_lines.append(f"[Error parsing JSON] {line}")
        except Exception as e:
            # Output any other errors with the raw line
            output_lines.append(f"[Error: {type(e).__name__}] {line}")

    return "\n\n".join(output_lines)


def format_json_object(data: Dict[str, Any]) -> str:
    """Format individual JSON object"""

    msg_type = data.get("type", "")

    if msg_type == "system" and data.get("subtype") == "init":
        return format_init(data)

    elif msg_type == "assistant":
        return format_assistant_message(data)

    elif msg_type == "user":
        return format_tool_result(data)

    elif msg_type == "result":
        return format_result(data)

    return ""


def format_init(data: Dict[str, Any]) -> str:
    """Format initialization message"""
    cwd = data.get("cwd", "")
    model = data.get("model", "")
    return f"Initializing: cwd={cwd}, model={model}"


def format_assistant_message(data: Dict[str, Any]) -> str:
    """Format assistant message"""
    message = data.get("message", {})
    content = message.get("content", [])

    if not content:
        return ""

    output_parts = []

    for item in content:
        if item.get("type") == "tool_use":
            tool_name = item.get("name", "")
            tool_input = item.get("input", {})
            output_parts.append(format_tool_use(tool_name, tool_input))

        elif item.get("type") == "text":
            text = item.get("text", "").strip()
            if text:
                output_parts.append(text)

    return "\n\n".join(output_parts)


def format_tool_use(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Format tool usage"""

    # Format based on tool type
    if tool_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        items = []
        for todo in todos:
            status_icon = "✓" if todo.get("status") == "completed" else "☐"
            todo_id = todo.get("id")
            content = todo.get("content")
            status = todo.get("status")
            items.append(f"  - [{todo_id}] {status_icon} {content} ({status})")
        return f"* {tool_name}(todos={len(todos)})\n" + "\n".join(items)

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        desc = tool_input.get("description", "")
        result = f'* {tool_name}("{command}")'
        if desc:
            result += f"\n  - Description: {desc}"
        return result

    elif tool_name == "WebSearch":
        query = tool_input.get("query", "")
        return f'* {tool_name}("{query}")'

    elif tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        return f'* {tool_name}("{file_path}")'

    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        old_str = tool_input.get("old_string", "").replace("\n", "\\n")[:50]
        new_str = tool_input.get("new_string", "").replace("\n", "\\n")[:50]
        return f'* {tool_name}("{file_path}")\n  - Before: {old_str}...\n  - After: {new_str}...'

    elif tool_name == "LS":
        path = tool_input.get("path", "")
        return f'* {tool_name}("{path}")'

    elif tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        return f'* {tool_name}("{pattern}")'

    elif tool_name == "Grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        return f'* {tool_name}("{pattern}", "{path}")'

    elif tool_name == "MultiEdit":
        file_path = tool_input.get("file_path", "")
        edits = tool_input.get("edits", [])
        result = f'* {tool_name}("{file_path}")'
        for i, edit in enumerate(edits[:3]):  # Show first 3 edits
            old_str = edit.get("old_string", "").replace("\n", "\\n")[:30]
            new_str = edit.get("new_string", "").replace("\n", "\\n")[:30]
            result += f"\n  - Edit {i + 1}: {old_str}... → {new_str}..."
        if len(edits) > 3:
            result += f"\n  - ... and {len(edits) - 3} more edits"
        return result

    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        preview = content[:50] + "..." if len(content) > 50 else content
        return f'* {tool_name}("{file_path}")\n  - Content: {preview}'

    elif tool_name == "NotebookRead":
        notebook_path = tool_input.get("notebook_path", "")
        return f'* {tool_name}("{notebook_path}")'

    elif tool_name == "NotebookEdit":
        notebook_path = tool_input.get("notebook_path", "")
        cell_number = tool_input.get("cell_number", "")
        return f'* {tool_name}("{notebook_path}", cell={cell_number})'

    elif tool_name == "WebFetch":
        url = tool_input.get("url", "")
        return f'* {tool_name}("{url}")'

    elif tool_name == "TodoRead":
        return f"* {tool_name}()"

    elif tool_name == "Task":
        description = tool_input.get("description", "")
        return f'* {tool_name}("{description}")'

    else:
        # Other tools
        params = ", ".join([f"{k}={repr(v)}" for k, v in tool_input.items()][:3])
        if len(tool_input) > 3:
            params += f", ... ({len(tool_input) - 3} more)"
        return f"* {tool_name}({params})"


def format_tool_result(data: Dict[str, Any]) -> str:
    """Format tool result"""
    message = data.get("message", {})
    content = message.get("content", [])

    if not content:
        return ""

    results = []
    for item in content:
        if item.get("type") == "tool_result":
            result_content = item.get("content", "")
            results.append(format_tool_result_content(result_content))

    return "\n\n".join(results)


def format_tool_result_content(content: str) -> str:
    """Format tool result content"""

    # Detect and format specific patterns
    if "On branch" in content and "git" in content.lower():
        lines = content.strip().split("\n")
        branch = lines[0] if lines else ""
        status_items = []
        for line in lines[1:]:
            if line.strip():
                status_items.append(f"  - {line.strip()}")
        result = f"Tool result: {branch}"
        if status_items:
            result += "\n" + "\n".join(status_items[:5])  # Show first 5 items
            if len(status_items) > 5:
                result += f"\n  - ... and {len(status_items) - 5} more items"
        return result

    elif "Web search results" in content:
        # Format web search results
        lines = content.strip().split("\n")
        title_line = lines[0] if lines else ""
        result = f"Tool result: {title_line}"

        # Extract links
        links_match = re.search(r"Links: \[(.*?)\]", content, re.DOTALL)
        if links_match:
            result += "\n  - Search results retrieved"

        # Extract key information
        if "not show any" in content or "not found" in content:
            result += "\n  - No matching package found"

        return result

    elif content.startswith("- /"):
        # LS command results
        lines = content.strip().split("\n")
        items = []
        for line in lines[:10]:  # Show first 10 items
            if line.strip().startswith("-"):
                items.append(f"  {line.strip()}")
        result = "Tool result: Directory contents retrieved"
        if items:
            result += "\n" + "\n".join(items)
        if len(lines) > 10:
            result += f"\n  ... and {len(lines) - 10} more items"
        return result

    elif re.match(r"^\s*\d+\t", content):
        # File content with line numbers
        lines = content.strip().split("\n")
        total_lines = len(lines)

        # Extract file summary
        summary_items = []
        for line in lines[:5]:
            match = re.match(r"\s*\d+\t(.+)", line)
            if match:
                content_line = match.group(1).strip()
                if content_line and not content_line.startswith("#"):
                    summary_items.append(f"  - {content_line}")

        result = f"Tool result: File content ({total_lines} lines)"
        if summary_items:
            result += "\n" + "\n".join(summary_items[:3])
        return result

    elif "has been updated" in content:
        # File update result
        lines = content.strip().split("\n")
        result = "Tool result: File updated successfully"
        for line in lines[:5]:  # Show first 5 lines
            if line.strip() and not line.startswith("The file"):
                result += f"\n  - {line.strip()}"
        return result

    else:
        # Other results
        lines = content.strip().split("\n")
        if len(lines) > 5:
            preview = "\n".join(lines[:3])
            return f"Tool result: {lines[0]}\n{preview}\n  ... ({len(lines) - 3} more lines)"
        else:
            return f"Tool result: {content.strip()}"


def format_result(data: Dict[str, Any]) -> str:
    """Format final result"""
    result_text = data.get("result", "")
    duration = data.get("duration_ms", 0) / 1000
    cost = data.get("cost_usd", 0)
    usage = data.get("usage", {})

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_tokens = cache_creation + cache_read
    total_tokens = input_tokens + output_tokens + cache_tokens

    output = result_text
    output += f"\n\nCompleted: duration={duration:.1f}s "
    output += f"cost=${cost:.3f} total_tokens={total_tokens:,}"

    return output
