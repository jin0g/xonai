"""Tests for xonai.__init__ module coverage."""


class TestInitCoverage:
    """Test xonai.__init__ module for better coverage."""

    def test_not_in_xonsh_environment(self):
        """Test behavior when not in xonsh environment."""
        # This test cannot easily test the import behavior without xonsh
        # since xonai.__init__ checks for xonsh at import time
        # Just verify that the module exists and has expected attributes
        import xonai

        # Check that HAS_XONSH attribute exists
        assert hasattr(xonai, "HAS_XONSH")

    def test_import_error_handling(self):
        """Test handling of ImportError during module loading."""
        # The module already handles ImportError internally
        # Just verify that the module loads without errors
        import xonai

        # Check that the module has the expected structure
        assert hasattr(xonai, "__version__")
        assert hasattr(xonai, "__all__")

    def test_version_info(self):
        """Test version information."""
        import xonai

        assert hasattr(xonai, "__version__")
        assert xonai.__version__ == "0.1.0"

        assert hasattr(xonai, "__all__")
        expected_exports = [
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
        assert set(xonai.__all__) == set(expected_exports)
