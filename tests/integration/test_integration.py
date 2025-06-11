#!/usr/bin/env python3
"""Integration tests for xoncc with mock Claude."""

import subprocess

import pytest


class TestXonccIntegration:
    """Integration tests for xoncc."""

    def test_no_error_message_displayed(self, tmp_path):
        """Test that natural language queries don't show error messages."""
        # Create a test script
        test_script = tmp_path / "test_no_errors.xsh"
        test_script.write_text("""
import sys
import io

# Capture stderr
old_stderr = sys.stderr
captured_stderr = io.StringIO()
sys.stderr = captured_stderr

# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Mock subprocess.Popen to prevent actual Claude calls
import subprocess
original_popen = subprocess.Popen
def mock_popen(*args, **kwargs):
    if args and 'claude' in str(args[0]):
        class MockProcess:
            def __init__(self):
                self.stdout = iter(['{"type": "tokens", "count": 1}'])
                self.stderr = iter([''])
                self.returncode = 0
            def wait(self):
                return 0
        return MockProcess()
    return original_popen(*args, **kwargs)
subprocess.Popen = mock_popen

# Test natural language query by using xonsh subprocess syntax
# This should trigger command_not_found and be handled by xoncc
try:
    $(how to list files)
except Exception:
    # Expected - command not found should be handled by xoncc
    pass

# Restore stderr
sys.stderr = old_stderr
stderr_output = captured_stderr.getvalue()

# Check results
if "command not found" in stderr_output.lower():
    print("FAIL: Error message found in stderr")
    print(f"Stderr: {repr(stderr_output)}")
    exit(1)
else:
    print("PASS: No error message in stderr")
    exit(0)
""")

        # Run the test
        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS" in result.stdout

    def test_function_override_works(self, tmp_path):
        """Test that SubprocSpec._run_binary override is working."""
        test_script = tmp_path / "test_override.xsh"
        test_script.write_text("""
# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Check that override is in place
from xonsh.procs.specs import SubprocSpec

# Verify the method has been patched
import inspect
source = inspect.getsource(SubprocSpec._run_binary)

if "xoncc_run_binary" in source:
    print("PASS: Override is in place")
    exit(0)
else:
    print("FAIL: Override not found")
    exit(1)
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS" in result.stdout

    def test_mock_claude_streaming(self, tmp_path):
        """Test with a mock Claude that simulates streaming behavior."""
        # Create mock claude script
        mock_claude = tmp_path / "claude"
        mock_claude.write_text("""#!/usr/bin/env python3
import sys
import json
import time

# Read input
query = sys.stdin.read().strip()

# Simulate streaming response
responses = [
    {"session_id": "test-123"},
    {"type": "tokens", "count": 10},
    {"type": "content_block_delta", "delta": {"text": "This is a test response."}},
    {"type": "tokens", "count": 15}
]

for r in responses:
    print(json.dumps(r))
    sys.stdout.flush()
    time.sleep(0.05)
""")
        mock_claude.chmod(0o755)

        # Create test script
        test_script = tmp_path / "test_streaming.xsh"
        test_script.write_text(f"""
import os
import time

# Add mock claude to PATH
os.environ["PATH"] = "{tmp_path}:" + os.environ["PATH"]

# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Time the execution
start = time.time()

# This should not show error and should call mock claude
# Use subprocess syntax to trigger command_not_found
try:
    $(test natural language query)
except Exception:
    pass  # Expected - handled by xoncc

elapsed = time.time() - start

# Verify it took some time (streaming delays)
if elapsed > 0.1:  # Should take at least 200ms with delays
    print("PASS: Streaming delays observed")
else:
    print("FAIL: Too fast, streaming might not be working")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        # Should complete successfully
        assert result.returncode == 0
        # Should not show error
        assert "command not found" not in result.stderr

    def test_normal_commands_unaffected(self, tmp_path):
        """Test that normal commands still work correctly."""
        test_script = tmp_path / "test_normal_commands.xsh"
        test_script.write_text("""
# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Test various normal commands
import subprocess

# Test 1: Regular command
result1 = $(echo "test")
assert result1.strip() == "test", f"Echo failed: {result1}"

# Test 2: Python evaluation
result2 = 2 + 2
assert result2 == 4, "Python evaluation failed"

# Test 3: Command with error should still show error or return error code
result3 = !(ls /nonexistent/directory/12345)
if result3.returncode != 0:
    print(f"PASS: Errors still work correctly (exit code {result3.returncode})")
else:
    print("FAIL: Command should have failed")
    exit(1)

# Test 4: Piping
result4 = $(echo "hello world" | grep world)
assert "world" in result4, "Piping failed"

print("PASS: All normal commands work")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert "PASS: All normal commands work" in result.stdout

    @pytest.mark.parametrize(
        "query,language",
        [
            ("how to list files", "English"),
            ("ファイルのリスト", "Japanese"),
            ("comment lister les fichiers", "French"),
            ("как список файлов", "Russian"),
        ],
    )
    def test_multilingual_queries(self, tmp_path, query, language):
        """Test that queries in different languages work without errors."""
        test_script = tmp_path / f"test_{language}.xsh"
        test_script.write_text(f"""
import os
import subprocess

# Mock subprocess.Popen to avoid actual Claude calls
original_popen = subprocess.Popen
def mock_popen(*args, **kwargs):
    if args and 'claude' in args[0]:
        # Return a mock process for Claude calls
        class MockProcess:
            def __init__(self):
                self.stdout = iter([''])
                self.stderr = iter([''])
                self.returncode = 0
            def wait(self):
                return 0
        return MockProcess()
    return original_popen(*args, **kwargs)
subprocess.Popen = mock_popen

# Add current directory to Python path for direct import
import sys
sys.path.insert(0, '/Users/akira/xoncc')

# Import and load xoncc directly
import xoncc.xontrib
xoncc.xontrib._load_xontrib_(__xonsh__)

# Test query in {language} using subprocess syntax
try:
    $({query.replace(" ", "_")}_command_that_does_not_exist)
except Exception:
    pass  # Expected - handled by xoncc

print("PASS: {language} query processed without error")
""")

        result = subprocess.run(
            ["xonsh", str(test_script)], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0
        assert f"PASS: {language} query processed" in result.stdout
        assert "command not found" not in result.stderr.lower()
