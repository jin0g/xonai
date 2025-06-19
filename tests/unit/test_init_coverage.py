"""Tests for xonai.__init__ module."""


class TestInitCoverage:
    """Test xonai.__init__ module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        import xonai

        # Module should import without errors
        assert xonai is not None

    def test_version_info(self):
        """Test version information."""
        import xonai

        # Should have version
        assert hasattr(xonai, "__version__")
        assert xonai.__version__ == "0.1.0"

    def test_module_structure(self):
        """Test basic module structure."""
        import xonai

        # Should have docstring
        assert xonai.__doc__ is not None
        assert "xonsh shell" in xonai.__doc__
