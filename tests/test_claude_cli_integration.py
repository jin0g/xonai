#!/usr/bin/env python3
"""Integration tests with dummy Claude CLI for comprehensive testing."""

import subprocess
import pytest
from unittest import mock


class TestClaudeCLIIntegration:
    """Tests with dummy Claude CLI integration."""

    def test_claude_cli_available(self, dummy_claude_env):
        """Test that Claude CLI is available in PATH."""
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            assert result.returncode == 0, "Claude CLI not found in PATH"
        except FileNotFoundError:
            pytest.skip("'which' command not available")

    def test_claude_cli_version(self, dummy_claude_env):
        """Test that Claude CLI responds to version check."""
        try:
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
            assert result.returncode == 0, f"Claude CLI version check failed: {result.stderr}"
            assert "dummy-claude" in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("Claude CLI version check timed out")
        except FileNotFoundError:
            pytest.skip("Claude CLI not found")

    def test_call_claude_direct_real(self, dummy_claude_env):
        """Test calling Claude directly with a simple query."""
        from xontrib.xoncc import call_claude_direct
        
        # This will call dummy Claude CLI
        try:
            call_claude_direct("test")
            # If we get here without exception, the test passed
            assert True
        except Exception as e:
            pytest.fail(f"Claude CLI integration failed: {e}")

    def test_auto_login_flow(self):
        """Test the auto-login flow detection."""
        from xontrib.xoncc import call_claude_direct
        
        # Mock a scenario where login is required
        with mock.patch('subprocess.Popen') as mock_popen:
            # First call: return login error
            mock_proc = mock.Mock()
            mock_proc.stdout = iter([
                '{"type":"assistant","message":{"content":[{"type":"text","text":"Invalid API key · Please run /login"}]}}'
            ])
            mock_proc.wait.return_value = 0
            mock_popen.return_value = mock_proc
            
            # This should trigger auto-login logic
            call_claude_direct("test query")
            
            # Verify that subprocess.Popen was called multiple times (original + login + retry)
            assert mock_popen.call_count >= 2


class TestClaudeCLIRealWorld:
    """Real-world integration tests that actually call Claude."""
    
    pytestmark = pytest.mark.claude_cli

    def test_simple_query(self):
        """Test a simple query to Claude."""
        from xontrib.xoncc import call_claude_direct
        
        # Capture output to verify it works
        import io
        import sys
        from unittest.mock import patch
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            call_claude_direct("What is 2+2? Please answer with just the number.")
        
        output = captured_output.getvalue()
        # We can't assert exact output since Claude's responses may vary
        # But we can assert that some output was produced
        assert len(output) > 0, "No output from Claude CLI call"

    def test_natural_language_command(self):
        """Test natural language command processing."""
        from xontrib.xoncc import handle_command_not_found
        
        # This should call Claude
        with mock.patch('xontrib.xoncc.call_claude_direct') as mock_claude:
            result = handle_command_not_found(["how", "do", "I", "list", "files"])
            
            # Verify Claude was called
            mock_claude.assert_called_once_with("how do I list files")
            # Verify error suppression
            assert result == {}

    def test_session_continuity(self):
        """Test that session ID is properly passed."""
        import xontrib.xoncc
        from xontrib.xoncc import call_claude_direct
        
        # Set a session ID
        xontrib.xoncc.CC_SESSION_ID = "test-session-integration"
        
        # Mock subprocess to check environment
        with mock.patch('subprocess.Popen') as mock_popen:
            mock_proc = mock.Mock()
            mock_proc.stdout = iter(['{"type":"assistant","message":{"content":[{"type":"text","text":"test"}]}}'])
            mock_proc.wait.return_value = 0
            mock_popen.return_value = mock_proc
            
            call_claude_direct("test query")
            
            # Check that environment was set
            call_kwargs = mock_popen.call_args[1]
            assert "env" in call_kwargs
            assert call_kwargs["env"]["CC_SESSION_ID"] == "test-session-integration"