"""Test xonai xontrib loading functionality."""

import sys
from unittest.mock import Mock, patch

import pytest

from xonai.xontrib import _load_xontrib_


class TestXontrib:
    """Test xonai xontrib loading."""

    def test_load_xontrib_already_loaded(self):
        """Test error when xontrib is already loaded."""

        # Create a real dict for ctx since Mock might not work with hasattr
        class MockXsh:
            def __init__(self):
                self.ctx = {"_xonai_loaded": True}

        mock_xsh = MockXsh()

        # Test - should raise RuntimeError
        with pytest.raises(RuntimeError, match="xonai xontrib is already loaded"):
            _load_xontrib_(mock_xsh)

    @patch("xonai.xontrib.xonai_run_binary_handler")
    def test_load_xontrib_success(self, mock_handler):
        """Test successful xontrib loading."""

        # Create a real dict for ctx
        class MockXsh:
            def __init__(self):
                self.ctx = {}

        mock_xsh = MockXsh()

        # Mock SubprocSpec
        mock_subproc_spec = Mock()
        original_run_binary = Mock()
        mock_subproc_spec._run_binary = original_run_binary

        # Create a mock module for xonsh.procs.specs
        mock_specs_module = Mock()
        mock_specs_module.SubprocSpec = mock_subproc_spec

        # Patch sys.modules to include the mock module
        with patch.dict(sys.modules, {"xonsh.procs.specs": mock_specs_module}):
            result = _load_xontrib_(mock_xsh)

        # Verify basic operation
        assert result == {}
        assert mock_xsh.ctx["_xonai_loaded"] is True

    def test_load_xontrib_import_error(self):
        """Test error handling when import fails."""

        class MockXsh:
            def __init__(self):
                self.ctx = {}

        mock_xsh = MockXsh()

        # Mock the import to raise ImportError
        def mock_import_error(*args, **kwargs):
            raise ImportError("No module named 'xonsh'")

        with patch("builtins.__import__", side_effect=mock_import_error):
            with pytest.raises(RuntimeError, match="Failed to setup xonai command interception"):
                _load_xontrib_(mock_xsh)

    def test_load_xontrib_sets_context(self):
        """Test that context is properly set."""

        class MockXsh:
            def __init__(self):
                self.ctx = {}

        mock_xsh = MockXsh()

        # Even if the import fails, the context should be set
        try:
            _load_xontrib_(mock_xsh)
        except RuntimeError:
            # Expected due to missing xonsh in test environment
            pass

        # The function should have marked itself as loaded
        assert mock_xsh.ctx.get("_xonai_loaded") is True
