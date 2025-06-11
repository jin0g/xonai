#!/usr/bin/env xonsh
# Debug script to check if function override is working

# Load xoncc xontrib
xontrib load xoncc

# Check if override is in place
from xonsh.procs.specs import SubprocSpec
print(f"SubprocSpec._run_binary method: {SubprocSpec._run_binary}")

# Check if it's our patched version
import inspect
source = inspect.getsource(SubprocSpec._run_binary)
print(f"Method source contains 'patched': {'patched' in source}")
print(f"Method source contains 'FileNotFoundError': {'FileNotFoundError' in source}")

# Test with a simple command
print("\n=== Testing override behavior ===")
try:
    # This should trigger our override
    $[nonexistentcommand999]
    print("Command executed without error")
except Exception as e:
    print(f"Exception caught: {type(e).__name__}: {e}")

# Check events
print(f"\nEvent handler registered: {__xonsh__.builtins.events.on_command_not_found}")