#!/usr/bin/env python3
"""
xoncc - Minimal Claude Code integration for xonsh

Simply catches command-not-found errors and asks Claude for help.
"""

from xoncc.claude import call_claude_direct


def _load_xontrib_(xsh, **kwargs):
    """Load the xontrib."""
    # Check if already loaded to prevent duplicates
    if hasattr(xsh.ctx, "_xoncc_loaded"):
        return {}

    # Mark as loaded
    xsh.ctx["_xoncc_loaded"] = True

    # Also add to builtins to prevent loading via other paths
    if not hasattr(xsh.builtins, "_xoncc_loaded"):
        xsh.builtins._xoncc_loaded = True

    # Override xonsh functions to intercept command execution
    try:
        import xonsh.tools as xt
        from xonsh.procs.specs import SubprocSpec

        # Store original method
        if not hasattr(SubprocSpec, "_xoncc_original_run_binary"):
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

                        return subprocess.Popen(
                            ["true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )

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
    from xoncc.claude import cli

    if "CC_SESSION_ID" in xsh.env:
        cli.CC_SESSION_ID = xsh.env["CC_SESSION_ID"]

    # Silent loading - no welcome message

    return {}
