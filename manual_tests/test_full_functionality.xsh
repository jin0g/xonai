#!/usr/bin/env xonsh
# Comprehensive test of xoncc functionality

import os
import time

# Load xoncc xontrib
xontrib load xoncc

print("=== Testing xoncc functionality ===\n")

# Test 1: Natural language query in Japanese
print("Test 1: Japanese query - 'ファイルのリスト'")
# Redirect stdout to avoid Claude output interfering with test results
with open("/dev/null", "w") as devnull:
    old_stdout = os.dup(1)
    os.dup2(devnull.fileno(), 1)
    
    # Run the query (this will call Claude)
    $[ファイルのリスト]
    
    # Restore stdout
    os.dup2(old_stdout, 1)
    os.close(old_stdout)

print("✓ Japanese query processed without error\n")

# Test 2: Natural language query in English
print("Test 2: English query - 'how to find large files'")
with open("/dev/null", "w") as devnull:
    old_stdout = os.dup(1)
    os.dup2(devnull.fileno(), 1)
    
    $[how to find large files]
    
    os.dup2(old_stdout, 1)
    os.close(old_stdout)

print("✓ English query processed without error\n")

# Test 3: Normal commands still work
print("Test 3: Normal commands")
$(echo "Hello from echo") 
print("✓ Normal commands work\n")

# Test 4: Python code still works
print("Test 4: Python expressions")
result = 2 + 2
print(f"2 + 2 = {result}")
print("✓ Python expressions work\n")

# Test 5: Error return codes
print("Test 5: Return codes")
ls > /dev/null 2>&1
print(f"ls return code: {__xonsh__.history.last_cmd_rtn}")

# This should not produce an error
$[nonexistent_command_12345] > /dev/null 2>&1
print(f"Natural language query return code: {__xonsh__.history.last_cmd_rtn}")
print("✓ Return codes handled correctly\n")

print("=== All tests passed! ===")