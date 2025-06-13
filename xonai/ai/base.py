"""Base classes for AI model implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator, Optional


class ContentType(Enum):
    """Content type of response."""

    TEXT = auto()
    JSON = auto()
    MARKDOWN = auto()


class ErrorType(Enum):
    """Error types for ErrorResponse."""

    NOT_LOGGED_IN = auto()
    CLI_NOT_FOUND = auto()
    NETWORK_ERROR = auto()


@dataclass
class Response:
    """Base class for all AI responses."""

    content: str
    content_type: ContentType = ContentType.TEXT


@dataclass
class InitResponse(Response):
    """Initialization response with session information."""

    session_id: Optional[str] = None
    model: Optional[str] = None

    def __post_init__(self):
        """Set default content type."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.TEXT


@dataclass
class MessageResponse(Response):
    """Text message response from AI."""

    def __post_init__(self):
        """Set default content type to MARKDOWN for Claude."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.MARKDOWN


@dataclass
class ToolUseResponse(Response):
    """Tool usage response."""

    tool: str = ""

    def __post_init__(self):
        """Set default content type."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.TEXT


@dataclass
class ToolResultResponse(Response):
    """Tool execution result response."""

    tool: str = ""

    def __post_init__(self):
        """Set default content type."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.TEXT


@dataclass
class ErrorResponse(Response):
    """Error response."""

    error_type: Optional[ErrorType] = None

    def __post_init__(self):
        """Set default content type."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.TEXT


@dataclass
class ResultResponse(Response):
    """Final result response with statistics."""

    token: int = 0

    def __post_init__(self):
        """Set default content type."""
        if not hasattr(self, "_content_type_set"):
            self.content_type = ContentType.TEXT


class BaseAI(ABC):
    """Base class for all AI model implementations."""

    @abstractmethod
    def __call__(self, prompt: str) -> Generator[Response, None, None]:
        """
        Process a prompt and yield responses.

        Args:
            prompt: The user's input prompt

        Yields:
            Response: Structured responses from the AI model
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the AI model."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI model is available and properly configured."""
        pass
