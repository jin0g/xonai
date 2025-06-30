"""
Command handling logic for xonai.

This module contains the actual implementation of command interception
and AI processing, separate from the xontrib registration.
"""

import os
import subprocess
import sys

from .agents import ClaudeAI, DummyAI
from .display import ResponseFormatter


def get_agent_instance():
    """Get appropriate AI instance based on environment."""
    if os.environ.get("XONAI_DUMMY") == "1":
        return DummyAI()
    else:
        return ClaudeAI()


def process_natural_language_query(query: str) -> None:
    """Process a natural language query through AI."""
    agent = get_agent_instance()
    formatter = ResponseFormatter()

    # Process the query through AI
    for response in agent(query):
        formatter.format(response)


def should_skip_command(args: list) -> bool:
    """Check if command should show normal error instead of AI processing."""
    if not args:
        return True

    # Skip common commands that should show normal errors
    skip_prefixes = ["ls", "cd", "pwd", "git", "python", "pip", "claude"]
    return any(args[0].startswith(prefix) for prefix in skip_prefixes)


def create_dummy_process():
    """Create a dummy successful process."""
    if sys.platform == "win32":
        cmd = ["cmd", "/c", "exit", "0"]
    else:
        cmd = ["true"]

    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def xonai_run_binary_handler(original_method, subprocess_spec, kwargs):
    """
    Handle command-not-found errors by processing through AI.

    Args:
        original_method: Original _run_binary method
        subprocess_spec: SubprocSpec instance
        kwargs: Keyword arguments for the subprocess

    Returns:
        subprocess.Popen: Either the original process or a dummy success process
    """
    try:
        import xonsh.tools as xt
    except ImportError:
        # Fallback for test environments without xonsh
        class MockXonshError(Exception):
            pass

        xt = type("MockXonshTools", (), {"XonshError": MockXonshError})()

    try:
        return original_method(subprocess_spec, kwargs)
    except xt.XonshError as ex:
        if "command not found" in str(ex):
            # Get the full command from self.args (preserves all characters)
            if hasattr(subprocess_spec, "args") and subprocess_spec.args:
                # Skip common commands (let them show normal errors)
                if should_skip_command(subprocess_spec.args):
                    raise ex

                # Join all arguments to get the full command
                full_command = " ".join(subprocess_spec.args)

                # Process as natural language query
                process_natural_language_query(full_command)

                # Return successful dummy process
                return create_dummy_process()

        # Re-raise all other errors
        raise ex
