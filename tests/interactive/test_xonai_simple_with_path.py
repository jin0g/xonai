#!/usr/bin/env python3
"""Simple manual test for xonai functionality with proper PATH."""

import os
import subprocess


def test_xonai_with_dummy():
    """Test xonai with dummy AI."""

    print("=== Testing xonai with Dummy AI ===\n")

    # Enable dummy AI mode
    env = os.environ.copy()
    env["XONAI_DUMMY"] = "1"

    print("Dummy AI mode enabled")

    # Test natural language queries
    print("\n1. Testing English query:")
    result = subprocess.run(
        'echo "how do I list files in current directory" | xonai',
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    print(f"   Exit code: {result.returncode}")
    print(f"   Output length: {len(result.stdout)} chars")
    print(f"   Error: {result.stderr[:100] if result.stderr else 'None'}")
    if result.stdout:
        print(f"   Output preview: {result.stdout[:300]}...")
        print(f"   Contains 'ls': {'ls' in result.stdout.lower()}")

    print("\n2. Testing Japanese query:")
    result = subprocess.run(
        'echo "Pythonでhello worldを表示する方法" | xonai',
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    print(f"   Exit code: {result.returncode}")
    print(f"   Output length: {len(result.stdout)} chars")
    print(f"   Error: {result.stderr[:100] if result.stderr else 'None'}")
    if result.stdout:
        print(f"   Output preview: {result.stdout[:300]}...")
        print(f"   Contains 'print': {'print' in result.stdout.lower()}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_xonai_with_dummy()
