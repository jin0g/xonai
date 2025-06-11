#!/usr/bin/env python3
"""Real-time JSON formatter for Claude streaming output"""

import json
import math
import sys
from typing import Any, Dict, Optional

from .tools import ToolFormatter


class RealtimeClaudeFormatter:
    """Formatter for real-time Claude JSON streaming output"""

    def __init__(self):
        self.total_tokens = 0
        self.cost = 0.0
        self.session_id = None
        self.last_line_length = 0
        self.displayed_content = set()  # Track displayed content to avoid duplicates
        self.is_streaming = False
        self.final_result_received = False
        self.tool_formatter = ToolFormatter()

        # Cost rates for Claude 3.5 Sonnet
        self.input_cost_per_token = 3.0 / 1000000  # $3 per million tokens
        self.output_cost_per_token = 15.0 / 1000000  # $15 per million tokens

    def clear_current_line(self):
        """Clear the current line"""
        print("\r", end="", flush=True)
        self.last_line_length = 0

    def update_token_display(self, tokens: int):
        """Update token count display and return cursor to start of line"""
        token_text = f" token: {tokens}..."
        print(f"{token_text}\r", end="", flush=True)
        self.last_line_length = len(token_text)

    def extract_content_from_json(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract and format all content from Claude JSON response"""
        # Skip the final result type to avoid duplicates
        if data.get("type") == "result":
            self.final_result_received = True
            return None

        # Handle system/init messages
        if data.get("type") == "system" and data.get("subtype") == "init":
            # Display available tools
            tools = data.get("tools", [])
            if tools:
                return f"🛠️  Available tools: {', '.join(tools)}\n"
            return None

        # Try tool formatting first
        for formatter_method in [
            self.tool_formatter.format_tool_use,
            self.tool_formatter.format_tool_result,
            self.tool_formatter.format_thinking,
        ]:
            result = formatter_method(data)
            if result:
                return result

        # Handle Claude Code specific format
        if data.get("type") == "assistant" and "message" in data:
            message = data["message"]
            if "content" in message and isinstance(message["content"], list):
                content_text = ""
                for content_item in message["content"]:
                    if content_item.get("type") == "text":
                        content_text += content_item.get("text", "")
                    elif content_item.get("type") == "tool_use":
                        tool_use = self.tool_formatter.format_tool_use(content_item)
                        if tool_use:
                            content_text += tool_use
                return content_text if content_text else None

        # Handle streaming content deltas
        elif data.get("type") == "content_block_delta":
            self.is_streaming = True
            if "delta" in data and "text" in data["delta"]:
                return data["delta"]["text"]

        # Handle content block start
        elif data.get("type") == "content_block_start":
            if "content_block" in data:
                content_block = data["content_block"]
                if content_block.get("type") == "text":
                    return content_block.get("text", "")
                elif content_block.get("type") == "tool_use":
                    return self.tool_formatter.format_tool_use(content_block)

        # Handle direct content
        elif "content" in data:
            return self._extract_direct_content(data["content"])

        # Handle progress and status updates
        elif data.get("type") == "progress":
            message = data.get("message", "")
            if message:
                return f"⏳ {message}\n"
        elif data.get("type") == "status":
            status = data.get("status", "")
            if status:
                return f"📊 {status}\n"

        return None

    def _extract_direct_content(self, content: Any) -> Optional[str]:
        """Extract content from various content formats"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    return item["text"]
                elif isinstance(item, str):
                    return item
                elif isinstance(item, dict) and item.get("type") == "tool_use":
                    return self.tool_formatter.format_tool_use(item)
        return None

    def extract_usage_info(self, data: Dict[str, Any]) -> None:
        """Extract token usage and cost information"""
        # Look for session ID
        if "session_id" in data:
            self.session_id = data["session_id"]

        # For result type, use the total_cost directly
        if data.get("type") == "result" and "cost_usd" in data:
            self.cost = data["cost_usd"]
            # Extract total tokens from usage
            if "usage" in data:
                self._update_token_count(data["usage"])
            return

        # For assistant messages, track token usage
        if data.get("type") == "assistant" and "message" in data:
            message = data["message"]
            if "usage" in message:
                self._update_token_count(message["usage"])
                # Calculate cost
                usage = message["usage"]
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                self.cost = input_tokens * self.input_cost_per_token
                self.cost += output_tokens * self.output_cost_per_token

    def _update_token_count(self, usage: Dict[str, Any]) -> None:
        """Update total token count from usage data"""
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_creation = usage.get("cache_creation_input_tokens", 0)
        cache_read = usage.get("cache_read_input_tokens", 0)
        cache_tokens = cache_creation + cache_read
        self.total_tokens = input_tokens + output_tokens + cache_tokens

    def process_json_line(self, line: str) -> bool:
        """Process a single JSON line and return True if content was displayed"""
        line = line.strip()
        if not line:
            return False

        try:
            data = json.loads(line)

            # Extract usage information first
            self.extract_usage_info(data)

            # Extract and display content
            content = self.extract_content_from_json(data)
            if content:
                self.clear_current_line()
                print(content, end="", flush=True)
                # Only show token count during streaming for content_block_delta
                if (
                    self.is_streaming
                    and data.get("type") == "content_block_delta"
                    and self.total_tokens > 0
                ):
                    self.update_token_display(self.total_tokens)
                return True

            # Don't show intermediate token displays
            return False

        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            self.clear_current_line()
            print(line, end="", flush=True)
            return True

    def finalize_output(self):
        """Print final summary"""
        # If we have a token display active, clear it and move to new line
        if self.last_line_length > 0:
            print()  # Move to next line
        else:
            # Ensure we're on a new line
            print()

        if self.total_tokens > 0 or self.cost > 0:
            # Use the actual cost from Claude if available
            if self.cost > 0:
                cost_str = f"${self.cost:.2f}"
            else:
                # Fallback calculation
                cost_cents = math.ceil(self.cost * 100) / 100
                cost_str = f"${cost_cents:.2f}"
            print(f"token: {self.total_tokens} cost: {cost_str}")

    def format_stream(self, input_stream):
        """Format Claude JSON stream in real-time"""
        try:
            for line in input_stream:
                self.process_json_line(line)

            self.finalize_output()

        except Exception as e:
            self.clear_current_line()
            print(f"\nError processing stream: {e}", file=sys.stderr)
