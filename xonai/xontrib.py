"""
xonai - AI integration for xonsh shell

Xontrib registration and setup for AI command interception.
"""

from .handler import xonai_run_binary_handler


def _load_xontrib_(xsh, **kwargs):
    """Load the xontrib."""
    # Ensure this is only loaded once
    if "_xonai_loaded" in xsh.ctx:
        raise RuntimeError("xonai xontrib is already loaded")

    # Mark as loaded
    xsh.ctx["_xonai_loaded"] = True

    # Override xonsh command execution to intercept command-not-found errors
    try:
        from xonsh.procs.specs import SubprocSpec

        # Store original method if not already stored
        if not hasattr(SubprocSpec, "_xonai_original_run_binary"):
            SubprocSpec._xonai_original_run_binary = SubprocSpec._run_binary

        def xonai_run_binary(self, kwargs):
            """Override _run_binary to intercept command-not-found errors."""
            return xonai_run_binary_handler(SubprocSpec._xonai_original_run_binary, self, kwargs)

        # Apply the override
        SubprocSpec._run_binary = xonai_run_binary

    except (ImportError, AttributeError) as e:
        # This is critical - if we can't override, xonai won't work
        raise RuntimeError(f"Failed to setup xonai command interception: {e}") from e

    return {}
