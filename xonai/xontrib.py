"""
xonai - AI integration for xonsh shell

Simply catches command-not-found errors and asks AI for help.
"""

import os

from .ai import ClaudeAI, DummyAI
from .display import ResponseFormatter


def _load_xontrib_(xsh, **kwargs):
    """Load the xontrib."""
    # Check if already loaded to prevent duplicates
    if hasattr(xsh.ctx, "_xonai_loaded"):
        return {}

    # Mark as loaded
    xsh.ctx["_xonai_loaded"] = True

    # Also add to builtins to prevent loading via other paths
    if not hasattr(xsh.builtins, "_xonai_loaded"):
        xsh.builtins._xonai_loaded = True

    # Initialize AI and formatter
    if os.environ.get("XONAI_DUMMY") == "1":
        ai = DummyAI()
    else:
        ai = ClaudeAI()

    formatter = ResponseFormatter()

    # Store in context for access
    xsh.ctx["_xonai_ai"] = ai
    xsh.ctx["_xonai_formatter"] = formatter

    # Override xonsh functions to intercept command execution
    try:
        import xonsh.tools as xt
        from xonsh.procs.specs import SubprocSpec

        # Store original method
        if not hasattr(SubprocSpec, "_xonai_original_run_binary"):
            SubprocSpec._xonai_original_run_binary = SubprocSpec._run_binary

        def xonai_run_binary(self, kwargs):
            """Override _run_binary to intercept command-not-found errors.

            When a command is not found, instead of showing an error,
            this function calls AI to interpret the natural language query.

            Args:
                self: SubprocSpec instance
                kwargs: Keyword arguments for the subprocess

            Returns:
                subprocess.Popen: Either the original process or a dummy success process
            """
            try:
                return SubprocSpec._xonai_original_run_binary(self, kwargs)
            except xt.XonshError as ex:
                if "command not found" in str(ex):
                    # Get the full command from self.args (preserves all characters)
                    if hasattr(self, "args") and self.args:
                        # Join all arguments to get the full command
                        full_command = " ".join(self.args)

                        # Skip common commands (let them show normal errors)
                        skip_prefixes = ["ls", "cd", "pwd", "git", "python", "pip", "claude"]
                        if any(self.args[0].startswith(prefix) for prefix in skip_prefixes):
                            raise ex

                        # This is a natural language query - call AI
                        import builtins

                        xsh = getattr(builtins, "__xonsh__", None)
                        ai = xsh.ctx.get("_xonai_ai")
                        formatter = xsh.ctx.get("_xonai_formatter")

                        if ai and formatter:
                            # Process the query through AI
                            for response in ai(full_command):
                                formatter.format(response)

                        # Return successful dummy process
                        import subprocess
                        import sys

                        if sys.platform == "win32":
                            cmd = ["cmd", "/c", "exit", "0"]
                        else:
                            cmd = ["true"]

                        return subprocess.Popen(
                            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )

                # Re-raise all other errors
                raise ex

        # Apply the override
        SubprocSpec._run_binary = xonai_run_binary

    except AttributeError as e:
        # This is critical - if we can't override, xonai won't work
        print(f"⚠️  Could not override _run_binary: {e}")
        import traceback

        traceback.print_exc()

    # Print loading message for interactive tests
    print("xonai loaded - natural language commands enabled")

    return {}
