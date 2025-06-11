"""
xoncc - Xonsh on Claude Code

This module loads the xoncc xontrib when imported in a xonsh shell.
"""

import importlib.util

__version__ = "0.0.1"
__author__ = "xoncc contributors"

# Import main functions if in xonsh
try:
    from .claude import is_claude_ready, open_claude_docs
except ImportError:
    # Not in proper environment, skip imports
    is_claude_ready = None
    open_claude_docs = None

__all__ = ["__version__", "is_claude_ready", "open_claude_docs"]

# Check if we're running in xonsh
HAS_XONSH = importlib.util.find_spec("xonsh") is not None

if HAS_XONSH:
    # Don't auto-load here to avoid conflicts with script loading
    # The xoncc script will handle loading the xontrib
    pass
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
