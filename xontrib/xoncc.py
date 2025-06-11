#!/usr/bin/env python3
"""
xoncc - Minimal Claude Code integration for xonsh

Simply catches command-not-found errors and asks Claude for help.
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

# Global session ID for resume functionality
CC_SESSION_ID: Optional[str] = None


def call_claude_direct(query: str) -> None:
    """Call Claude directly with auto-login handling."""
    global CC_SESSION_ID

    # Check if Claude CLI is installed
    try:
        result = subprocess.run(["which", "claude"], capture_output=True, text=True)
        if result.returncode != 0:
            # Claude CLI not found, show installation guide
            try:
                from xoncc.check_claude import open_claude_docs

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
        cmd = ["claude", "--print", "--verbose", "--output-format", "stream-json", query]

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
                ["claude", "/exit"],
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


def handle_command_not_found(cmd: List[str], **kwargs) -> Optional[bool]:
    """Handle command not found events."""
    # Skip if it's trying to run claude itself (avoid recursion)
    if cmd and len(cmd) > 0 and cmd[0] == "claude":
        # Return None to let xonsh handle it normally
        return None

    # Join command parts
    command_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)

    # Skip common typos and shell-like commands
    prefixes = ["ls", "cd", "pwd", "git", "python", "pip"]
    if any(command_str.startswith(prefix) for prefix in prefixes):
        return None

    # Call Claude silently
    call_claude_direct(command_str)

    # Return True to suppress the default error
    return True


def _load_xontrib_(xsh, **kwargs):
    """Load the xontrib."""
    # Check if already loaded to prevent duplicates
    if hasattr(xsh.ctx, '_xoncc_loaded'):
        return {}
    
    # Mark as loaded
    xsh.ctx['_xoncc_loaded'] = True
    
    # Also add to builtins to prevent loading via other paths
    if not hasattr(xsh.builtins, '_xoncc_loaded'):
        xsh.builtins._xoncc_loaded = True
    
    # Override xonsh functions to intercept command execution
    try:
        from xonsh.procs.specs import SubprocSpec
        import xonsh.tools as xt
        
        # Store original method
        if not hasattr(SubprocSpec, '_xoncc_original_run_binary'):
            SubprocSpec._xoncc_original_run_binary = SubprocSpec._run_binary
        
        def xoncc_run_binary(self, kwargs):
            """xoncc override for _run_binary."""
            try:
                return SubprocSpec._xoncc_original_run_binary(self, kwargs)
            except xt.XonshError as ex:
                if "command not found" in str(ex):
                    # Extract command name from error
                    import re
                    match = re.search(r"command not found: '([^']+)'", str(ex))
                    if match:
                        cmd_name = match.group(1)
                        
                        # Skip common commands (let them show normal errors)
                        skip_prefixes = ["ls", "cd", "pwd", "git", "python", "pip", "claude"]
                        if any(cmd_name.startswith(prefix) for prefix in skip_prefixes):
                            raise ex
                        
                        # This is a natural language query - call Claude silently
                        call_claude_direct(cmd_name)
                        
                        # Return successful dummy process
                        import subprocess
                        return subprocess.Popen(['true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Re-raise all other errors
                raise ex
        
        # Apply the override
        SubprocSpec._run_binary = xoncc_run_binary
        
    except Exception as e:
        print(f"⚠️  Could not override _run_binary: {e}")
        import traceback
        traceback.print_exc()

    # Add convenience functions to xonsh globals
    xsh.ctx["cc"] = lambda query: call_claude_direct(query)
    xsh.ctx["claude"] = lambda query: call_claude_direct(query)

    # Set up session management
    global CC_SESSION_ID
    if "CC_SESSION_ID" in xsh.env:
        CC_SESSION_ID = xsh.env["CC_SESSION_ID"]

    # Silent loading - no welcome message

    return {}
