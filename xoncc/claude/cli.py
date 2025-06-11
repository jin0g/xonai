#!/usr/bin/env python3
"""Claude CLI integration functions."""

import json
import os
import subprocess
from typing import Optional

# Global session ID for resume functionality
CC_SESSION_ID: Optional[str] = None


def call_claude_direct(query: str) -> None:
    """Call Claude directly with auto-login handling."""
    global CC_SESSION_ID

    # Check if we should use dummy Claude
    if os.environ.get("XONCC_DUMMY") == "1":
        claude_cmd = "dummy_claude"
    else:
        claude_cmd = "claude"

    # Check if Claude CLI is installed
    try:
        result = subprocess.run(["which", claude_cmd], capture_output=True, text=True)
        if result.returncode != 0:
            # Claude CLI not found, show installation guide
            try:
                from .check import open_claude_docs

                print("Claude CLI is not installed.")
                print("Opening installation guide...")
                open_claude_docs()
                return
            except ImportError:
                print("Error: 'claude' command not found. Please install Claude CLI.")
                return
    except Exception:
        print("Error: 'claude' command not found. Please install Claude CLI.")
        return

    try:
        # Build command with streaming JSON output
        cmd = [claude_cmd, "--print", "--verbose", "--output-format", "stream-json", query]

        # Add session ID if available
        env = os.environ.copy()
        if CC_SESSION_ID:
            env["CC_SESSION_ID"] = CC_SESSION_ID

        # Use subprocess.Popen for streaming output
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=0,  # Unbuffered for real-time output
        )

        # Process streaming output and check for login errors
        login_error_detected = False

        # Import formatter for real-time display
        try:
            from xoncc.formatters import format_claude_json_stream

            # Process streaming output
            for line in proc.stdout:
                line = line.rstrip()
                if line:  # Skip empty lines
                    try:
                        data = json.loads(line)

                        # Check for login error
                        if (
                            data.get("type") == "assistant"
                            and data.get("message", {}).get("content")
                            and any(
                                "Invalid API key" in str(content.get("text", ""))
                                for content in data["message"]["content"]
                                if isinstance(content, dict)
                            )
                        ):
                            login_error_detected = True
                            break

                        format_claude_json_stream(line)
                    except json.JSONDecodeError:
                        # Non-JSON output, print as-is (only if not empty)
                        if line.strip():
                            print(line)
        except ImportError:
            # Fallback: print raw output directly
            for line in proc.stdout:
                line = line.rstrip()
                if line:  # Skip empty lines
                    if "Invalid API key" in line:
                        login_error_detected = True
                        break
                    print(line)

        # Wait for completion
        proc.wait()

        # If login error detected, prompt for login and retry
        if login_error_detected:
            print("\nClaude CLI requires login. Launching login process...")

            # Run claude /exit to trigger login and immediately exit
            login_proc = subprocess.Popen(
                [claude_cmd, "/exit"],
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            login_proc.wait()

            print("Login completed. Retrying your request...")

            # Retry the original command
            retry_proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True, bufsize=0
            )

            # Process retry output
            try:
                from xoncc.formatters import format_claude_json_stream

                for line in retry_proc.stdout:
                    line = line.rstrip()
                    if line:  # Skip empty lines
                        try:
                            data = json.loads(line)
                            format_claude_json_stream(line)
                        except json.JSONDecodeError:
                            if line.strip():
                                print(line)
            except ImportError:
                for line in retry_proc.stdout:
                    line = line.rstrip()
                    if line:  # Skip empty lines
                        print(line)

            retry_proc.wait()

    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully
        print("\n\nInterrupted by user")
        if "proc" in locals():
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                proc.kill()
    except FileNotFoundError:
        print("Error: 'claude' command not found. Please install Claude CLI.")
    except Exception as e:
        print(f"Error calling Claude: {e}")
