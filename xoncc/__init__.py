"""
xoncc - Xonsh on Claude Code

This module loads the xoncc xontrib when imported in a xonsh shell.
"""

import importlib.util

__version__ = "0.0.1"
__author__ = "xoncc contributors"

# Check if we're running in xonsh
HAS_XONSH = importlib.util.find_spec("xonsh") is not None

if HAS_XONSH:
    # We're in xonsh, load the xontrib automatically
    import sys

    if hasattr(sys, "__xonsh__"):
        # Use xonsh's built-in xontrib loading
        import builtins

        xonsh = getattr(builtins, "__xonsh__", None)
        if xonsh:
            xonsh.execer.exec("""xontrib load xoncc""", glbs=xonsh.ctx)
else:
    # Not in xonsh, provide a helpful message
    def _not_in_xonsh():
        raise RuntimeError(
            "xoncc can only be used within a xonsh shell. "
            "Please install xonsh and run 'import xoncc' "
            "from within a xonsh session."
        )

    # Make all attributes raise an error
    def __getattr__(name):
        _not_in_xonsh()
