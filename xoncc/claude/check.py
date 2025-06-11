#!/usr/bin/env python3
"""Check if Claude CLI is installed and logged in."""

import subprocess
import sys


def is_claude_ready():
    """Check if Claude CLI is installed and logged in.

    Returns:
        tuple: (is_ready: bool, status: str)
        - status can be: "ready", "not_installed", "not_logged_in"
    """
    # Check if we should use dummy Claude
    import os

    if os.environ.get("XONCC_DUMMY") == "1":
        claude_cmd = "dummy_claude"
    else:
        claude_cmd = "claude"

    # Check if claude command exists
    try:
        result = subprocess.run(["which", claude_cmd], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "not_installed"
    except Exception:
        return False, "not_installed"

    # Check if logged in by running a simple command
    try:
        result = subprocess.run(
            [claude_cmd, "--print", "--output-format", "stream-json", "/exit"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Check for login-related errors in output
        if "Invalid API key" in result.stdout or "Invalid API key" in result.stderr:
            return False, "not_logged_in"

        return True, "ready"
    except subprocess.TimeoutExpired:
        return True, "ready"  # Assume ready if it doesn't exit quickly
    except Exception:
        return False, "not_installed"


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


if __name__ == "__main__":
    # Test the check
    ready, status = is_claude_ready()
    if ready:
        print("Claude CLI is ready!")
    else:
        print(f"Claude CLI status: {status}")
        if status == "not_installed":
            print("Opening installation guide...")
            open_claude_docs()
