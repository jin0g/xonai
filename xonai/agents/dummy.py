"""Dummy AI implementation for testing."""

import time
from collections.abc import Generator

from .base import (
    BaseAI,
    InitResponse,
    MessageResponse,
    Response,
    ResultResponse,
    ToolResultResponse,
    ToolUseResponse,
)


class DummyAI(BaseAI):
    """Dummy AI implementation for testing purposes."""

    def __init__(self, delay: float = 0.1):
        """
        Initialize Dummy AI.

        Args:
            delay: Delay between yielding responses (simulates streaming)
        """
        self.delay = delay
        self._session_counter = 0
        self._last_tool: str = ""  # Track last tool for ToolResultResponse

    @property
    def name(self) -> str:
        """Return the name of this AI model."""
        return "Dummy"

    @property
    def is_available(self) -> bool:
        """Dummy AI is always available."""
        return True

    def __call__(self, prompt: str) -> Generator[Response, None, None]:
        """
        Process a prompt and yield dummy responses.

        Args:
            prompt: The user's input prompt

        Yields:
            Response: Dummy responses for testing
        """
        # Simulate session initialization
        self._session_counter += 1
        yield InitResponse(
            content="Dummy AI",
            session_id=f"dummy-session-{self._session_counter}",
            model="dummy-model",
        )
        time.sleep(self.delay)

        # Simulate streaming message response
        response_text = f"I received your prompt: '{prompt}'. This is a dummy response."
        words = response_text.split()

        for i, word in enumerate(words):
            yield MessageResponse(
                content=word + (" " if i < len(words) - 1 else ""),
            )
            time.sleep(self.delay)

        # Simulate tool usage
        if "file" in prompt.lower() or "search" in prompt.lower():
            tool_name = "Grep"
            self._last_tool = tool_name
            yield ToolUseResponse(
                content="search pattern in files",
                tool=tool_name,
            )
            time.sleep(self.delay)

            yield ToolResultResponse(
                content="Found 3 matching files",
                tool=self._last_tool,
            )
            time.sleep(self.delay)

        # Simulate completion
        duration_ms = int((len(words) + 3) * self.delay * 1000)
        cost_usd = 0.001
        input_tokens = len(prompt.split())
        output_tokens = len(response_text.split())
        total_tokens = input_tokens + output_tokens

        yield ResultResponse(
            content=(
                f"duration_ms={duration_ms}, cost_usd={cost_usd:.6f}, "
                f"input_tokens={input_tokens}, output_tokens={output_tokens}"
            ),
            token=total_tokens,
        )
