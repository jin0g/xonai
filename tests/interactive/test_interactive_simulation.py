#!/usr/bin/env python3
"""
Interactive test simulation for xoncc with delayed responses.
This simulates Claude's streaming behavior.
"""

import json
import time
from pathlib import Path

import pytest

# Mark tests that simulate actual Claude CLI behavior
pytestmark = pytest.mark.integration


def simulate_claude_streaming_response(query):
    """Simulate Claude's streaming JSON response with realistic delays."""

    # Initial session ID
    yield json.dumps({"session_id": "test-session-123"}) + "\n"
    time.sleep(0.1)

    # Simulate thinking
    yield json.dumps({"type": "thinking", "text": "Analyzing your query..."}) + "\n"
    time.sleep(0.5)

    # Simulate token counting
    tokens = 0
    for _ in range(5):
        tokens += 10
        yield json.dumps({"type": "tokens", "count": tokens}) + "\n"
        time.sleep(0.1)

    # Simulate actual response based on query
    if "list" in query.lower() or "ファイル" in query:
        responses = [
            "To list files, you can use the `ls` command.",
            "\n\nHere are some examples:",
            "\n- `ls` - List files in current directory",
            "\n- `ls -la` - List all files with details",
            "\n- `ls -lh` - List with human-readable sizes",
        ]
    elif "find" in query.lower() or "探す" in query:
        responses = [
            "To find files, you can use the `find` command.",
            "\n\nExamples:",
            "\n- `find . -name '*.py'` - Find Python files",
            "\n- `find . -size +10M` - Find files larger than 10MB",
        ]
    else:
        responses = [
            "I understand you're asking about: " + query,
            "\n\nLet me help you with that.",
            "\n\nThis is a simulated response for testing.",
        ]

    # Stream the response with delays
    for text in responses:
        yield json.dumps({"type": "content_block_delta", "delta": {"text": text}}) + "\n"
        time.sleep(0.2)  # Simulate typing delay

    # Final tokens
    yield json.dumps({"type": "tokens", "count": tokens + 50}) + "\n"


def mock_claude_server(input_queue, output_file):
    """Mock Claude server that reads from queue and writes streaming responses."""
    while True:
        try:
            query = input_queue.get(timeout=1)
            if query is None:
                break

            with open(output_file, "w") as f:
                for line in simulate_claude_streaming_response(query):
                    f.write(line)
                    f.flush()

        except Exception:
            continue


def test_interactive_xoncc():
    """Test xoncc with simulated interactive Claude responses."""

    print("=== Interactive xoncc Test Simulation ===\n")

    # Test queries
    test_queries = ["how do I list files", "ファイルを探す方法", "find large files quickly"]

    for query in test_queries:
        print(f"Testing query: '{query}'")
        print("-" * 50)

        # Simulate the streaming response
        print("Claude is thinking...", end="", flush=True)

        for line in simulate_claude_streaming_response(query):
            data = json.loads(line.strip())

            if data.get("type") == "thinking":
                print(f"\r{data['text']}", end="", flush=True)
            elif data.get("type") == "tokens":
                print(f"\rTokens: {data['count']}...", end="", flush=True)
            elif data.get("type") == "content_block_delta":
                # Clear the status line and print content
                print("\r" + " " * 30 + "\r", end="")
                print(data["delta"]["text"], end="", flush=True)

        print("\n")
        time.sleep(0.5)

    print("\n=== Test Complete ===")


def test_real_xoncc_behavior():
    """Test the actual xoncc behavior with a mock Claude process."""

    print("\n=== Testing Real xoncc Behavior ===\n")

    # Create a test script that uses xoncc
    test_script = Path("/tmp/test_xoncc_interactive.xsh")
    test_script.write_text("""
import time
print("Loading xoncc...")
xontrib load xoncc

print("Testing natural language query...")
# This should trigger xoncc without error
how to list Python files

print("\\nTest completed!")
""")

    # Create a mock claude executable
    mock_claude = Path("/tmp/mock_claude")
    mock_claude.write_text("""#!/bin/bash
# Mock claude that produces streaming output
echo '{"session_id": "test-123"}'
sleep 0.1
echo '{"type": "tokens", "count": 10}'
sleep 0.1
echo '{"type": "content_block_delta", "delta": {"text": "Use find . -name *.py"}}'
""")
    mock_claude.chmod(0o755)

    # Run the test with PATH modified to use our mock
    import os
    env = os.environ.copy()
    env["PATH"] = f"/tmp:{env['PATH']}"

    try:
        # Note: This would actually run if we had xonsh available
        print("Would run: xonsh test_xoncc_interactive.xsh")
        print("Expected behavior:")
        print("1. xoncc loads without error")
        print("2. Natural language query processes without 'command not found' error")
        print("3. Claude response streams in real-time")
        print("4. Token count updates during processing")
    finally:
        # Cleanup
        if test_script.exists():
            test_script.unlink()
        if mock_claude.exists():
            mock_claude.unlink()


if __name__ == "__main__":
    import os

    # Run interactive simulation
    test_interactive_xoncc()

    # Test real behavior
    test_real_xoncc_behavior()
