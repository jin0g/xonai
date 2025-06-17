#!/usr/bin/env xonsh
# Test script to verify error elimination with function override

import sys
import io
from contextlib import redirect_stderr

# Load xoncc xontrib
xontrib load xoncc

# Test 1: Capture stderr to check if error messages appear
print("=== Test 1: Natural language query ===")

# Capture stderr
old_stderr = sys.stderr
captured_stderr = io.StringIO()
sys.stderr = captured_stderr

# Test natural language query
$[これはテストです]

# Restore stderr and check captured output
sys.stderr = old_stderr
stderr_content = captured_stderr.getvalue()

print(f"Captured stderr: {repr(stderr_content)}")
if "command not found" in stderr_content.lower():
    print("FAIL: Error message still appears in stderr")
else:
    print("PASS: No error message in stderr")

# Test 2: Check return code
print("\n=== Test 2: Return code test ===")
# This should not cause shell to report error
ls > /dev/null 2>&1 || echo "ls succeeded"
nonexistentcommand123 > /dev/null 2>&1 || echo "nonexistent command failed as expected"

print("\n=== Test 3: Direct command test ===")
# This should trigger xoncc without error
echo "Testing natural language: how to list files"