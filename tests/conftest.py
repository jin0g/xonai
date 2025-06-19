"""
Pytest configuration for xonai tests.
"""

import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# TestEnvironment no longer needed with new AI architecture

# Add the parent directory to sys.path so we can import xontrib
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def xonsh_executable():
    """Get the path to the xonsh executable."""
    # First try to find xonsh in PATH
    xonsh_path = shutil.which("xonsh")
    if xonsh_path:
        return xonsh_path

    # If not found, try to construct from current Python executable
    # This works when xonsh is installed in the same environment as pytest
    python_bin_dir = Path(sys.executable).parent
    xonsh_in_venv = python_bin_dir / "xonsh"
    if xonsh_in_venv.exists():
        return str(xonsh_in_venv)

    # Last resort - assume it's xonsh and let subprocess fail with clear error
    return "xonsh"


@pytest.fixture
def xonai_executable():
    """Get the path to the xonai executable."""
    # First try to find xonai in PATH
    xonai_path = shutil.which("xonai")
    if xonai_path:
        return xonai_path

    # If not found, try to construct from current Python executable
    # This works when xonai is installed in the same environment as pytest
    python_bin_dir = Path(sys.executable).parent
    xonai_in_venv = python_bin_dir / "xonai"
    if xonai_in_venv.exists():
        return str(xonai_in_venv)

    # Last resort - assume it's xonai and let subprocess fail with clear error
    return "xonai"


@pytest.fixture
def mock_xonsh_env(monkeypatch):
    """Mock xonsh environment for testing."""

    # Create mock XonshSession
    mock_xsh = MagicMock()
    mock_xsh.aliases = {}
    mock_xsh.env = {
        "USER": "testuser",
        "PWD": "/test/dir",
        "CC_MAX_LOG_SIZE": "10000",
        "CLAUDE_CAPTURE_OUTPUT": "1",
    }
    mock_xsh.ctx = {}

    # Mock events
    mock_events = MagicMock()
    mock_events.on_command_not_found = MagicMock()
    mock_events.on_postcommand = MagicMock()

    # Mock execer for xsh file execution
    mock_execer = MagicMock()
    mock_execer.exec = MagicMock()
    mock_xsh.execer = mock_execer

    # Create a mock built_ins module
    mock_built_ins = MagicMock()
    mock_built_ins.XSH = mock_xsh

    # Patch imports
    monkeypatch.setattr("xonsh.built_ins", mock_built_ins)
    monkeypatch.setattr("xonsh.built_ins.XSH", mock_xsh)
    monkeypatch.setattr("builtins.aliases", mock_xsh.aliases)
    monkeypatch.setattr("builtins.events", mock_events)
    monkeypatch.setattr("builtins.__xonsh__", mock_xsh)

    # Mock the dollar sign operations
    class MockDollar:
        def __init__(self, env):
            self.env = env

        def __getattr__(self, name):
            return self.env.get(name, "")

        def __setattr__(self, name, value):
            if name != "env":
                self.env[name] = value
            else:
                super().__setattr__(name, value)

        def __contains__(self, name):
            return name in self.env

        def __getitem__(self, name):
            return self.env[name]

    monkeypatch.setattr("builtins.__xonsh__.env", mock_xsh.env)

    return mock_xsh


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess for testing Claude command execution."""
    from unittest.mock import MagicMock

    mock_popen = MagicMock()
    mock_process = MagicMock()
    mock_process.communicate.return_value = ('{"type": "result", "subtype": "success"}', "")
    mock_popen.return_value = mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    return mock_popen


@pytest.fixture
def dummy_ai_env(monkeypatch):
    """Setup test environment with dummy AI."""
    # Enable dummy AI mode
    monkeypatch.setenv("XONAI_DUMMY", "1")
    yield
