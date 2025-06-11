#!/usr/bin/env python3
"""
Dummy Claude CLI implementation for testing.
Simulates Claude CLI behavior without requiring actual API access.
"""

import argparse
import json
import sys
import time


def simulate_streaming_response(query: str, output_format: str = "text"):
    """Simulate a streaming response from Claude."""

    # Predefined responses for common test queries
    responses = {
        "hello": "Hello! How can I help you today?",
        "what is 2+2": "2 + 2 = 4",
        "how do I list files": "You can list files using the `ls` command.",
        "test": "This is a test response from dummy Claude.",
        "hello world": "Hello, World! This is a test response.",
        "help": "I'm a dummy Claude implementation for testing purposes.",
    }

    # Find matching response
    response = responses.get(query.lower().strip(), f"This is a dummy response for: {query}")

    if output_format == "stream-json":
        # Simulate streaming JSON output like real Claude CLI

        # Initial system message
        yield {
            "type": "system",
            "subtype": "init",
            "cwd": "/test/directory",
            "session_id": "test-session-123",
            "tools": ["Task", "Bash", "Read", "Write"],
            "mcp_servers": [],
            "model": "claude-sonnet-4-test",
            "permissionMode": "default",
            "apiKeySource": "test",
        }

        # Simulate thinking
        yield {
            "type": "assistant",
            "message": {
                "id": "test-msg-123",
                "model": "claude-sonnet-4-test",
                "role": "assistant",
                "type": "message",
                "content": [{"type": "text", "text": ""}],
            },
            "parent_tool_use_id": None,
            "session_id": "test-session-123",
        }

        # Stream the response word by word
        words = response.split()
        current_text = ""

        for word in words:
            current_text += word + " "

            # Simulate content delta
            yield {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": word + " "},
            }

            # Small delay to simulate streaming
            time.sleep(0.05)

        # Final message with complete response
        yield {
            "type": "assistant",
            "message": {
                "id": "test-msg-456",
                "model": "claude-sonnet-4-test",
                "role": "assistant",
                "stop_reason": "end_turn",
                "type": "message",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": len(words),
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
                "content": [{"type": "text", "text": current_text.strip()}],
            },
            "session_id": "test-session-123",
        }

        # Result summary
        yield {
            "type": "result",
            "subtype": "success",
            "cost_usd": 0.001,
            "is_error": False,
            "duration_ms": 500,
            "duration_api_ms": 300,
            "num_turns": 1,
            "result": current_text.strip(),
            "session_id": "test-session-123",
            "total_cost": 0.001,
            "usage": {
                "input_tokens": 10,
                "output_tokens": len(words),
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        }
    else:
        # Plain text output
        yield {"text": response}


def main():
    parser = argparse.ArgumentParser(description="Dummy Claude CLI for testing")
    parser.add_argument("--print", action="store_true", help="Print mode")
    parser.add_argument(
        "--output-format", choices=["text", "stream-json"], default="text", help="Output format"
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("query", nargs="?", help="Query to process")

    args = parser.parse_args()

    if args.version:
        print("dummy-claude 1.0.0 (test implementation)")
        return

    if not args.query:
        # Interactive mode (simplified)
        print("Dummy Claude CLI - Interactive mode")
        print("Type your queries or 'exit' to quit")

        while True:
            try:
                query = input(">>> ").strip()
                if query.lower() in ["exit", "quit", "/exit"]:
                    break

                for response in simulate_streaming_response(query, args.output_format):
                    if args.output_format == "stream-json":
                        print(json.dumps(response, separators=(",", ":")))
                    else:
                        print(response.get("text", ""))

            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except EOFError:
                break
    else:
        # Single query mode
        try:
            for response in simulate_streaming_response(args.query, args.output_format):
                if args.output_format == "stream-json":
                    print(json.dumps(response, separators=(",", ":")))
                    sys.stdout.flush()
                else:
                    print(response.get("text", ""))

        except KeyboardInterrupt:
            print("\nInterrupted", file=sys.stderr)
            sys.exit(130)


if __name__ == "__main__":
    main()
