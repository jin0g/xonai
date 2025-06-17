#!/usr/bin/env python3
"""
Shell script wrapper for cc command
"""

import subprocess
import sys
from pathlib import Path


def cc_command():
    """Legacy function name for compatibility"""
    main()


def main():
    """Execute the cc command via shell script"""
    script_path = Path(__file__).parent / "cc.sh"

    if not script_path.exists():
        print("Error: cc.sh script not found", file=sys.stderr)
        sys.exit(1)

    # Execute the shell script, preserving stdin/stdout/stderr
    try:
        result = subprocess.run(
            [str(script_path)], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing cc.sh: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
