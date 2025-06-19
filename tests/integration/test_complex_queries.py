"""Test complex AI queries that might cause subprocess issues."""

import pytest

from xonai.ai import ClaudeAI
from xonai.ai.base import ErrorResponse, InitResponse, ResultResponse


@pytest.mark.claude_cli
@pytest.mark.integration
class TestComplexQueries:
    """Test complex queries that might cause subprocess deadlocks."""

    def test_project_overview_japanese(self):
        """Test Japanese query for project overview that causes heavy Claude output."""
        ai = ClaudeAI()
        if not ai.is_available:
            pytest.skip("Claude CLI not available")

        # This query often causes Claude to output a lot of data
        query = "このプロジェクトの概要を把握して下さい"

        responses = list(ai(query))

        # Should have at least init and result
        assert len(responses) >= 2

        # Check for proper response types
        has_init = any(isinstance(r, InitResponse) for r in responses)
        has_result = any(isinstance(r, ResultResponse) for r in responses)

        assert has_init, "Should have InitResponse"
        assert has_result, "Should have ResultResponse"

        # Should not have uncaught errors
        error_responses = [r for r in responses if isinstance(r, ErrorResponse)]
        for error in error_responses:
            # Only network or login errors are acceptable
            assert error.error_type in [None, "NOT_LOGGED_IN", "NETWORK_ERROR"], (
                f"Unexpected error: {error.content}"
            )

    def test_complex_multiline_query(self):
        """Test complex multiline query that might cause buffer issues."""
        ai = ClaudeAI()
        if not ai.is_available:
            pytest.skip("Claude CLI not available")

        # Complex multiline query
        query = """Please analyze this codebase and provide:
1. A comprehensive overview of the project structure
2. List all main components and their relationships
3. Identify key design patterns used
4. Suggest potential improvements
5. Create a detailed summary of functionality"""

        responses = list(ai(query))

        # Should complete without deadlock
        assert len(responses) >= 2

        # Check for proper completion
        has_init = any(isinstance(r, InitResponse) for r in responses)
        has_result = any(isinstance(r, ResultResponse) for r in responses)

        assert has_init
        assert has_result

    def test_rapid_fire_queries(self):
        """Test multiple queries in quick succession."""
        ai = ClaudeAI()
        if not ai.is_available:
            pytest.skip("Claude CLI not available")

        queries = [
            "What is 2+2?",
            "List Python built-in functions",
            "Explain decorators",
        ]

        for query in queries:
            responses = list(ai(query))

            # Each query should complete successfully
            assert len(responses) >= 2
            has_result = any(isinstance(r, ResultResponse) for r in responses)
            assert has_result, f"Query '{query}' did not complete"

    def test_unicode_heavy_query(self):
        """Test query with lots of unicode that might cause encoding issues."""
        ai = ClaudeAI()
        if not ai.is_available:
            pytest.skip("Claude CLI not available")

        # Unicode-heavy query
        query = "説明して: 🚀 📖 ✏️ 🔧 🌐 🔍 📋 📝 これらの絵文字の意味"

        responses = list(ai(query))

        # Should handle unicode properly
        assert len(responses) >= 2

        # Should not have encoding errors
        error_responses = [r for r in responses if isinstance(r, ErrorResponse)]
        for error in error_responses:
            assert "encoding" not in error.content.lower()
            assert "decode" not in error.content.lower()
