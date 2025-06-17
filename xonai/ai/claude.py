"""Claude AI implementation for xonai."""

import json
import os
import shutil
import subprocess
import sys
from typing import Generator, Optional

from .base import (
    BaseAI,
    ErrorResponse,
    ErrorType,
    InitResponse,
    MessageResponse,
    Response,
    ResultResponse,
    ToolResultResponse,
    ToolUseResponse,
)


class ClaudeAI(BaseAI):
    """Claude AI implementation using Claude CLI."""

    def __init__(self):
        """Initialize Claude AI."""
        self._claude_cmd = "dummy_claude" if os.environ.get("XONAI_DUMMY") == "1" else "claude"
        self._last_tool = None  # Track last tool for ToolResultResponse

    @property
    def name(self) -> str:
        """Return the name of this AI model."""
        return "Claude"

    @property
    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        return shutil.which(self._claude_cmd) is not None

    def __call__(self, prompt: str) -> Generator[Response, None, None]:
        """
        Process a prompt using Claude CLI and yield responses.

        Args:
            prompt: The user's input prompt

        Yields:
            Response: Structured responses from Claude
        """
        if not self.is_available:
            yield ErrorResponse(
                content="Claude CLI not found. Please install Claude CLI.",
                error_type=ErrorType.CLI_NOT_FOUND,
            )
            return

        try:
            # Build command with streaming JSON output
            cmd = [
                self._claude_cmd,
                "--print",
                "--verbose",
                "--output-format",
                "stream-json",
                prompt,
            ]

            # Use subprocess.Popen for streaming output
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
            )

            # Process streaming output
            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        response = self._parse_claude_response(data)
                        if response:
                            yield response
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

            # Check for stderr output (errors)
            if proc.stderr:
                stderr_output = proc.stderr.read()
                if stderr_output:
                    # Check for specific error types
                    error_text = stderr_output.strip()
                    error_type = None
                    if "not logged in" in error_text.lower():
                        error_type = ErrorType.NOT_LOGGED_IN
                    elif "network" in error_text.lower() or "connection" in error_text.lower():
                        error_type = ErrorType.NETWORK_ERROR

                    yield ErrorResponse(
                        content=error_text,
                        error_type=error_type,
                    )

            # Wait for completion and check exit code
            exit_code = proc.wait()
            if exit_code != 0:
                yield ErrorResponse(
                    content=f"Claude CLI exited with code {exit_code}",
                    error_type=None,  # Unexpected error
                )

        except KeyboardInterrupt:
            # Handle Ctrl-C gracefully
            if "proc" in locals():
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()
            yield ErrorResponse(content="Interrupted by user", error_type=None)
        except Exception as e:
            yield ErrorResponse(
                content=f"Unexpected error: {str(e)}",
                error_type=None,
            )

    def _parse_claude_response(self, data: dict) -> Optional[Response]:
        """
        Parse Claude CLI JSON output into Response.

        Args:
            data: JSON data from Claude CLI

        Returns:
            Response or None if the data should be skipped
        """
        # Parse based on 'type' field in the JSON
        msg_type = data.get("type", "")

        if msg_type == "system" and data.get("subtype") == "init":
            # INIT message with session info
            return InitResponse(
                content="Claude Code",
                session_id=data.get("session_id", ""),
                model=data.get("model", "unknown"),
            )

        elif msg_type == "content_block_delta":
            # Streaming text content
            delta = data.get("delta", {})
            text = delta.get("text", "")
            if text:
                return MessageResponse(content=text)

        elif msg_type == "assistant":
            # Assistant message (may contain text or tool use)
            message = data.get("message", {})
            content = message.get("content", [])

            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "").strip()
                    if text:
                        # Add newline before assistant messages
                        return MessageResponse(content=f"\n{text}")
                elif item.get("type") == "tool_use":
                    # Tool usage
                    tool_name = item.get("name", "unknown")
                    tool_input = item.get("input", {})

                    # Track last tool
                    self._last_tool = tool_name

                    # Extract content based on tool
                    content = tool_name
                    if tool_name == "Bash":
                        content = tool_input.get("command", "")
                    elif tool_name in ["Read", "NotebookRead"]:
                        content = (
                            tool_input.get("file_path", "")
                            or tool_input.get("notebook_path", "")
                        )
                    elif tool_name in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
                        content = (
                            tool_input.get("file_path", "")
                            or tool_input.get("notebook_path", "")
                        )
                    elif tool_name == "WebSearch":
                        content = tool_input.get("query", "")
                    elif tool_name == "WebFetch":
                        content = tool_input.get("url", "")
                    elif tool_name in ["Glob", "Grep"]:
                        pattern = tool_input.get("pattern", "")
                        path = tool_input.get("path", "")
                        content = f"{pattern} in {path}" if path else pattern
                    elif tool_name == "Task":
                        content = tool_input.get("description", "")
                    elif tool_name == "LS":
                        path = tool_input.get("path", "")
                        ignore = tool_input.get("ignore", [])
                        if ignore:
                            content = f"{path} (ignore: {', '.join(ignore)})"
                        else:
                            content = path

                    return ToolUseResponse(
                        content=content,
                        tool=tool_name,
                    )

        elif msg_type == "user":
            # User message (tool results)
            content = data.get("message", {}).get("content", [])

            for item in content:
                if item.get("type") == "tool_result":
                    result_content = item.get("content", "")
                    return ToolResultResponse(
                        content=result_content,
                        tool=self._last_tool or "",
                    )

        elif msg_type == "error":
            # Error message
            error = data.get("error", {})
            message = error.get("message", data.get("message", "Unknown error"))

            # Try to determine error type
            error_type = None
            if "not logged in" in message.lower():
                error_type = ErrorType.NOT_LOGGED_IN
            elif "network" in message.lower() or "connection" in message.lower():
                error_type = ErrorType.NETWORK_ERROR

            return ErrorResponse(
                content=message,
                error_type=error_type,
            )

        elif msg_type == "result":
            # Final result with stats
            usage = data.get("usage", {})
            duration_ms = data.get("duration_ms", 0)
            cost_usd = data.get("cost_usd", 0)
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            # Format content string
            content = (
                f"duration_ms={duration_ms}, cost_usd={cost_usd:.6f}, "
                f"input_tokens={input_tokens}, output_tokens={output_tokens}"
            )

            # Calculate total tokens for next session
            total_tokens = input_tokens + output_tokens

            return ResultResponse(
                content=content,
                token=total_tokens,
            )

        # Skip other types
        return None


def open_claude_docs():
    """Open Claude documentation in browser."""
    url = "https://docs.anthropic.com/en/docs/claude-code/getting-started"

    if sys.platform == "darwin":  # macOS
        subprocess.run(["open", url])
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", url])
    elif sys.platform == "win32":
        subprocess.run(["start", url], shell=True)
    else:
        print(f"Please visit: {url}")
