#!/usr/bin/env python3
"""Test AI response functionality with real Claude CLI."""

import subprocess

import pytest


class TestAIResponse:
    """Test AI response functionality."""

    def test_ai_integration_no_errors(self, tmp_path):
        """Test that AI queries don't show command not found errors."""
        # Create simple mock claude
        mock_claude = tmp_path / "claude"
        mock_claude.write_text("""#!/usr/bin/env python3
import json
import sys

# Simple response that will be formatted
response = {"type": "content_block_delta", "delta": {"text": "AI response received"}}
print(json.dumps(response))
""")
        mock_claude.chmod(0o755)

        # Create test script
        test_script = tmp_path / "test_ai_integration.xsh"
        test_script.write_text(f"""
import os

# Add mock claude to PATH
os.environ["PATH"] = "{tmp_path}:" + os.environ["PATH"]

# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Test AI query - should not show "command not found"
try:
    $(hello_world_test)
except Exception:
    pass  # Expected - handled by xoncc

print("PASS: AI integration test")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS: AI integration test" in result.stdout
        # Most importantly: should NOT contain command not found error
        assert "command not found" not in result.stderr.lower()

    def test_function_override_prevents_errors(self, tmp_path):
        """Test that function override prevents command not found errors."""
        test_script = tmp_path / "test_override.xsh"
        test_script.write_text("""
# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Mock subprocess.Popen to avoid calling real Claude
import subprocess
original_popen = subprocess.Popen
def mock_popen(*args, **kwargs):
    if args and 'claude' in str(args[0]):
        class MockProcess:
            def __init__(self):
                self.stdout = iter(['{"type": "tokens", "count": 1}'])
                self.stderr = iter([''])
            def wait(self): return 0
        return MockProcess()
    return original_popen(*args, **kwargs)
subprocess.Popen = mock_popen

# Test that command not found doesn't show error
try:
    $(nonexistent_command_for_ai)
except Exception:
    pass  # Should be handled by override

print("PASS: Function override working")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS: Function override working" in result.stdout
        # Should NOT show command not found error
        assert "command not found" not in result.stderr.lower()

    def test_normal_commands_still_work(self, tmp_path):
        """Test that normal commands are not affected by the override."""
        test_script = tmp_path / "test_normal_commands.xsh"
        test_script.write_text("""
# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Test normal commands still work
result = $(echo "hello")
assert result.strip() == "hello"

# Test that actual file errors still show up
import subprocess
try:
    subprocess.run(['ls', '/nonexistent/path'], check=True)
    print("FAIL: Should have raised error")
except subprocess.CalledProcessError:
    print("PASS: Normal errors still work")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS: Normal errors still work" in result.stdout

    @pytest.mark.skipif(
        "not hasattr(subprocess, 'run')"
    )  # Skip if testing environment lacks subprocess
    def test_real_claude_integration(self, tmp_path):
        """Test integration with real Claude CLI if available."""
        # Check if real Claude CLI is available
        try:
            claude_check = subprocess.run(["claude", "--help"], capture_output=True, timeout=5)
            if claude_check.returncode != 0:
                pytest.skip("Real Claude CLI not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Real Claude CLI not available or too slow")

        # Create test script for real Claude
        test_script = tmp_path / "test_real_claude.xsh"
        test_script.write_text("""
# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Test simple query
try:
    $(test)
except Exception:
    pass  # Expected - handled by xoncc

print("PASS: Real Claude integration test")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=30
        )

        assert result.returncode == 0
        assert "PASS: Real Claude integration test" in result.stdout
        # Real Claude should provide some response (we can't predict exact content)
        # But we can verify no error messages appear
        assert "command not found" not in result.stderr.lower()
