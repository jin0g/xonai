#!/usr/bin/env python3
"""
xoncc v2 - Cleaner implementation as pure xontrib
"""

import os
import subprocess
import sys
from typing import List, Optional

# Global session ID
CC_SESSION_ID: Optional[str] = None


def call_claude_simple(query: str) -> Optional[str]:
    """Simple Claude caller that returns output."""
    try:
        # Direct subprocess call for better control
        result = subprocess.run(
            ["claude"],
            input=query.encode(),
            capture_output=True,
            text=True,
            env={**os.environ, "CC_SESSION_ID": CC_SESSION_ID} if CC_SESSION_ID else None,
        )

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Claude error: {result.stderr}", file=sys.stderr)
            return None

    except FileNotFoundError:
        print("Error: 'claude' command not found. Please install Claude CLI.", file=sys.stderr)
        return None
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return None


def xoncc_handler(cmd: List[str], **kwargs) -> None:
    """Enhanced command not found handler."""
    # Get the full command as string
    command_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)

    # Check if we should handle this
    # Skip if it looks like a typo of common commands
    if command_str.startswith(("ls", "cd", "pwd", "git", "python")):
        return None  # Let xonsh handle it normally

    # Call Claude
    print(f"🤔 Asking Claude about: {command_str}")
    response = call_claude_simple(command_str)

    if response:
        print(response)

        # Optionally execute suggested commands
        # This could be enhanced with user confirmation
        # execute_suggestion(response)

    # Return empty dict to suppress default error
    return {}


def _load_xontrib_(xsh, **kwargs):
    """Load xontrib - minimal and clean."""
    # Only use the official event system
    xsh.builtins.events.on_command_not_found(xoncc_handler)

    # Add helper functions to builtins
    xsh.builtins.cc = call_claude_simple
    xsh.builtins.claude = call_claude_simple

    print("🚀 xoncc loaded - natural language commands enabled")
    print("💡 Tip: You can also use cc('query') or claude('query') directly")

    return {}
