#!/usr/bin/env python3
"""Simple manual test for xonai functionality."""

import os
import subprocess


def test_xonai_manually():
    """Manually test xonai commands."""

    print("=== Testing xonai Functionality ===\n")

    # Test 1: Bash commands
    print("1. Testing bash command execution:")
    result = subprocess.run(
        'echo "echo Hello from bash" | xonai', shell=True, capture_output=True, text=True
    )
    print(f"   Output: {result.stdout}")
    print(f"   Success: {'Hello from bash' in result.stdout}")

    # Test 2: Python code
    print("\n2. Testing Python code execution:")
    result = subprocess.run(
        'echo "print(42 * 2)" | xonai', shell=True, capture_output=True, text=True
    )
    print(f"   Output: {result.stdout}")
    print(f"   Success: {'84' in result.stdout}")

    # Test 3: Natural language with dummy Claude
    print("\n3. Testing natural language with dummy Claude:")
    env = os.environ.copy()
    env["XONAI_DUMMY"] = "1"

    # English query
    print("\n   a) English query:")
    result = subprocess.run(
        'echo "how do I list files" | xonai', shell=True, capture_output=True, text=True, env=env
    )
    print(f"      Output length: {len(result.stdout)} chars")
    print(f"      Contains 'ls': {'ls' in result.stdout.lower()}")
    print(f"      First 200 chars: {result.stdout[:200]}...")

    # Japanese query
    print("\n   b) Japanese query:")
    result = subprocess.run(
        'echo "ファイルを一覧表示する方法" | xonai',
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    print(f"      Output length: {len(result.stdout)} chars")
    print(f"      Contains response: {len(result.stdout) > 50}")
    print(f"      First 200 chars: {result.stdout[:200]}...")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_xonai_manually()
