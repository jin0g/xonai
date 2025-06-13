"""
xonai - AI integration for xonsh shell

This module loads the xonai xontrib when imported in a xonsh shell.
"""

import importlib.util
from typing import TYPE_CHECKING

__version__ = "0.1.0"
__author__ = "xonai contributors"

# Import main classes if available
if TYPE_CHECKING:
    from .ai import (
        BaseAI,
        ClaudeAI,
        ContentType,
        DummyAI,
        ErrorResponse,
        InitResponse,
        MessageResponse,
        Response,
        ResultResponse,
        ToolResultResponse,
        ToolUseResponse,
    )
    from .display import ResponseFormatter
else:
    try:
        from .ai import (
            BaseAI,
            ClaudeAI,
            ContentType,
            DummyAI,
            ErrorResponse,
            InitResponse,
            MessageResponse,
            Response,
            ResultResponse,
            ToolResultResponse,
            ToolUseResponse,
        )
        from .display import ResponseFormatter
    except ImportError:
        # Not in proper environment, skip imports
        Response = None  # type: ignore
        BaseAI = None  # type: ignore
        ContentType = None  # type: ignore
        ClaudeAI = None  # type: ignore
        DummyAI = None  # type: ignore
        ResponseFormatter = None  # type: ignore
        InitResponse = None  # type: ignore
        MessageResponse = None  # type: ignore
        ToolUseResponse = None  # type: ignore
        ToolResultResponse = None  # type: ignore
        ErrorResponse = None  # type: ignore
        ResultResponse = None  # type: ignore

__all__ = [
    "__version__",
    "Response",
    "BaseAI",
    "ContentType",
    "InitResponse",
    "MessageResponse",
    "ToolUseResponse",
    "ToolResultResponse",
    "ErrorResponse",
    "ResultResponse",
    "ClaudeAI",
    "DummyAI",
    "ResponseFormatter",
]

# Check if we're running in xonsh
HAS_XONSH = importlib.util.find_spec("xonsh") is not None

if not HAS_XONSH:
    # Not in xonsh, provide a helpful message
    def _not_in_xonsh():
        raise RuntimeError(
            "xonai can only be used within a xonsh shell. "
            "Please install xonsh and run 'xontrib load xonai' "
            "from within a xonsh session."
        )

    # Make all attributes raise an error
    def __getattr__(name):
        _not_in_xonsh()
