#!/usr/bin/env python3
"""
Setup test environment with dummy Claude CLI.
This script creates a temporary PATH that includes our dummy claude command.
"""

import os
import shutil
import tempfile
from pathlib import Path


class TestEnvironment:
    """Context manager for test environment with dummy Claude CLI."""

    def __init__(self):
        self.temp_dir = None
        self.original_path = None
        self.dummy_claude_path = None

    def __enter__(self):
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="xoncc_test_")
        self.dummy_claude_path = Path(self.temp_dir) / "claude"

        # Copy dummy claude script
        test_dir = Path(__file__).parent
        dummy_claude_source = test_dir / "dummy_claude.py"

        # Create executable claude script
        with open(self.dummy_claude_path, "w") as f:
            f.write(f'#!/bin/bash\npython3 {dummy_claude_source} "$@"\n')

        os.chmod(self.dummy_claude_path, 0o755)

        # Modify PATH to include our dummy claude
        self.original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{self.temp_dir}:{self.original_path}"

        print(f"Test environment setup: dummy claude at {self.dummy_claude_path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original PATH
        if self.original_path is not None:
            os.environ["PATH"] = self.original_path

        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        print("Test environment cleaned up")


def setup_test_environment():
    """Setup test environment programmatically."""
    return TestEnvironment()


if __name__ == "__main__":
    # Test the setup
    with setup_test_environment() as env:
        # Verify dummy claude works
        result = os.system("claude --version")
        if result == 0:
            print("✓ Dummy Claude CLI setup successful")
        else:
            print("✗ Dummy Claude CLI setup failed")
            exit(1)
