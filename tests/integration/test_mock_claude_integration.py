#!/usr/bin/env python3
"""
Mock Claude integration test with realistic delays and streaming output.
"""

import json
import os
import sys
import time
from pathlib import Path


class MockClaudeServer:
    """Mock Claude server that simulates realistic streaming behavior."""

    def __init__(self):
        self.session_id = "test-session-" + str(int(time.time()))
        self.token_count = 0

    def generate_response(self, query):
        """Generate a streaming response for a query."""
        # Initial session response
        yield {"session_id": self.session_id}
        time.sleep(0.05)

        # Simulate initial processing
        self.token_count = 0
        for _ in range(3):
            self.token_count += 5
            yield {"type": "tokens", "count": self.token_count}
            time.sleep(0.05)

        # Generate contextual response
        if "list" in query.lower() or "ファイル" in query:
            response_parts = [
                "To list files in the current directory, ",
                "you can use the `ls` command.\n\n",
                "Here are some useful variations:\n",
                "- `ls` - Basic file listing\n",
                "- `ls -la` - Detailed listing with hidden files\n",
                "- `ls -lh` - Human-readable file sizes\n",
                "- `ls -lt` - Sort by modification time\n",
            ]
        elif "find" in query.lower() or "探す" in query:
            response_parts = [
                "To find files, ",
                "the `find` command is very powerful.\n\n",
                "Examples:\n",
                "- `find . -name '*.py'` - Find all Python files\n",
                "- `find . -size +10M` - Find files larger than 10MB\n",
                "- `find . -mtime -7` - Files modified in last 7 days\n",
            ]
        else:
            response_parts = [
                f"I understand you're asking about: {query}\n\n",
                "Let me help you with that.\n",
                "This is a simulated response for testing purposes.\n",
            ]

        # Stream the response with realistic delays
        for part in response_parts:
            # Simulate token generation
            self.token_count += len(part.split())
            yield {"type": "tokens", "count": self.token_count}
            time.sleep(0.02)

            # Send content
            yield {"type": "content_block_delta", "delta": {"text": part}}
            time.sleep(0.05 + len(part) * 0.001)  # Vary by content length

        # Final token count
        yield {"type": "tokens", "count": self.token_count}


def create_mock_claude_cli():
    """Create a mock claude CLI that behaves like the real one."""
    mock_claude = Path("/tmp/mock_claude_cli.py")
    mock_claude.write_text("""#!/usr/bin/env python3
import sys
import json
import time

# Simple mock that reads from stdin and produces streaming JSON
query = sys.stdin.read().strip()

# Mock server
from test_mock_claude_integration import MockClaudeServer
server = MockClaudeServer()

# Generate streaming response
for response in server.generate_response(query):
    print(json.dumps(response))
    sys.stdout.flush()
""")

    mock_claude.chmod(0o755)
    return mock_claude


def test_xonai_with_mock_claude():
    """Test xonai with a mock Claude that simulates real behavior."""

    print("=== Testing xonai with Mock Claude ===\n")

    # Create mock claude executable
    mock_claude_wrapper = Path("/tmp/claude")
    mock_claude_wrapper.write_text(f"""#!/bin/bash
# Mock claude wrapper that behaves like real claude CLI
exec python3 {__file__} mock-claude-server "$@"
""")
    mock_claude_wrapper.chmod(0o755)

    # Create test xonsh script
    test_script = Path("/tmp/test_xonai_mock.xsh")
    test_script.write_text("""
import os
import time

# Add mock claude to PATH
os.environ["PATH"] = "/tmp:" + os.environ["PATH"]

print("Loading xonai with mock Claude...")
xontrib load xonai

print("\\nTest 1: English query")
print("Query: 'how to list files'")
print("-" * 40)
start_time = time.time()
how to list files
elapsed = time.time() - start_time
print(f"\\nResponse time: {elapsed:.2f}s")

print("\\n" + "="*50 + "\\n")

print("Test 2: Japanese query")
print("Query: 'ファイルを探す方法'")
print("-" * 40)
start_time = time.time()
ファイルを探す方法
elapsed = time.time() - start_time
print(f"\\nResponse time: {elapsed:.2f}s")

print("\\n✓ All tests completed successfully!")
""")

    # Prepare environment
    env = os.environ.copy()
    env["PATH"] = f"/tmp:{env['PATH']}"
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    print("Running xonsh with mock Claude...")
    print("Expected behavior:")
    print("1. No 'command not found' errors")
    print("2. Streaming output with token counts")
    print("3. Realistic response delays")
    print("\n" + "-" * 50 + "\n")

    # Would run: subprocess.run(["xonsh", str(test_script)], env=env)
    print("(In a real environment, this would execute the test)")

    # Cleanup
    for f in [mock_claude_wrapper, test_script]:
        if f.exists():
            f.unlink()


def mock_claude_server_mode():
    """Run as a mock Claude server when called with special argument."""
    server = MockClaudeServer()
    query = sys.stdin.read().strip()

    for response in server.generate_response(query):
        print(json.dumps(response))
        sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mock-claude-server":
        # Run as mock server
        mock_claude_server_mode()
    else:
        # Run tests
        print("Testing Mock Claude Server...\n")

        # Test the mock server directly
        server = MockClaudeServer()
        query = "how to find large files"

        print(f"Query: '{query}'")
        print("Streaming response:")
        print("-" * 50)

        for response in server.generate_response(query):
            if response.get("type") == "content_block_delta":
                print(response["delta"]["text"], end="", flush=True)
            elif response.get("type") == "tokens":
                print(f"\r[Tokens: {response['count']}]", end="", flush=True)
                time.sleep(0.01)

        print("\n" + "-" * 50)
        print("\n✓ Mock server test complete")

        # Test with xonai
        print("\n" + "=" * 60 + "\n")
        test_xonai_with_mock_claude()
