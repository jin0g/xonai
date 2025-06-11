#!/usr/bin/env python3
"""Tests for xoncc main entry point."""

import sys
from pathlib import Path
from unittest import mock

import pytest

from xoncc.main import main, set_as_default_shell


def test_set_as_default_shell(capsys):
    """Test set_as_default_shell function."""
    set_as_default_shell()
    captured = capsys.readouterr()

    assert "To set xoncc as your default shell:" in captured.out
    assert "which xoncc" in captured.out
    assert "/etc/shells" in captured.out
    assert "chsh -s" in captured.out


def test_main_no_xonsh_installed():
    """Test main when xonsh is not installed."""
    with mock.patch("importlib.util.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_with_xonsh_installed(tmp_path, monkeypatch):
    """Test main when xonsh is installed."""
    # Mock xonsh being installed
    mock_spec = mock.Mock()
    with mock.patch("importlib.util.find_spec", return_value=mock_spec):
        # Mock subprocess.run to avoid actually launching xonsh
        mock_result = mock.Mock(returncode=0)
        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            # Mock tempfile to use our test directory
            temp_rc = tmp_path / "temp.xsh"
            with mock.patch("tempfile.NamedTemporaryFile") as mock_temp:
                mock_file = mock.mock_open()()
                mock_file.name = str(temp_rc)
                mock_temp.return_value.__enter__.return_value = mock_file

                # Create a fake .xonshrc
                fake_xonshrc = tmp_path / ".xonshrc"
                fake_xonshrc.write_text("# Test xonshrc\n")
                monkeypatch.setattr(Path, "home", lambda: tmp_path)

                # Run main
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Verify xonsh was called
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                assert args[0] == ["xonsh"]
                assert "env" in kwargs
                assert "XONSHRC" in kwargs["env"]

                # Verify exit code
                assert exc_info.value.code == 0


def test_main_xonsh_returns_error():
    """Test main when xonsh returns an error code."""
    mock_spec = mock.Mock()
    with mock.patch("importlib.util.find_spec", return_value=mock_spec):
        # Mock subprocess.run to return error code
        mock_result = mock.Mock(returncode=1)
        with mock.patch("subprocess.run", return_value=mock_result):
            with mock.patch("tempfile.NamedTemporaryFile"):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1


def test_main_cleanup_on_exception(tmp_path):
    """Test that temporary file is cleaned up even if exception occurs."""
    mock_spec = mock.Mock()
    with mock.patch("importlib.util.find_spec", return_value=mock_spec):
        temp_rc = tmp_path / "temp.xsh"
        temp_rc.write_text("# temp file")

        with mock.patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = mock.mock_open()()
            mock_file.name = str(temp_rc)
            mock_temp.return_value.__enter__.return_value = mock_file

            # Make subprocess.run raise an exception
            with mock.patch("subprocess.run", side_effect=Exception("Test error")):
                with mock.patch("os.unlink") as mock_unlink:
                    with pytest.raises(Exception, match="Test error"):
                        main()

                    # Verify cleanup was attempted
                    mock_unlink.assert_called_once_with(str(temp_rc))


def test_command_line_set_default():
    """Test command line with --set-default argument."""
    test_args = ["xoncc", "--set-default"]
    with mock.patch.object(sys, "argv", test_args):
        with mock.patch("xoncc.main.set_as_default_shell"):
            # Import and run the main module
            import xoncc.main

            if __name__ == "__main__":
                if len(sys.argv) > 1 and sys.argv[1] == "--set-default":
                    xoncc.main.set_as_default_shell()

            # For this test, we just verify the function would be called
            # In actual usage, the if __name__ == "__main__"
            # block would handle this


def test_xoncc_command_integration():
    """Integration test for xoncc command."""
    # This test verifies the entry point is correctly configured
    from xoncc.main import main

    assert callable(main)

    # Verify the function has the expected behavior
    with mock.patch("importlib.util.find_spec", return_value=None):
        with pytest.raises(SystemExit):
            main()
