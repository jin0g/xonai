"""
Pytest configuration for xoncc tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.dummy_claude.setup_test_env import TestEnvironment

# Add the parent directory to sys.path so we can import xontrib
sys.path.insert(0, str(Path(__file__).parent.parent))


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
def dummy_claude_env():
    """Setup test environment with dummy Claude CLI."""
    with TestEnvironment() as env:
        yield env
