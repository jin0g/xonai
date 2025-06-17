#!/usr/bin/env python3
"""xoncc - Xonsh on Claude Code main entry point."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point for xoncc shell."""
    # Check if xonsh is installed
    try:
        import importlib.util

        if importlib.util.find_spec("xonsh") is None:
            raise ImportError
    except ImportError:
        print("Error: xonsh is not installed.", file=sys.stderr)
        print("Please install xonsh first: pip install xonsh", file=sys.stderr)
        sys.exit(1)

    # Set up xonsh with xoncc loaded
    xonshrc_path = Path.home() / ".xonshrc"

    # Create temporary xonshrc that loads xoncc
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xsh", delete=False) as f:
        temp_rc = f.name

        # Load user's existing xonshrc if it exists
        if xonshrc_path.exists():
            f.write(f"source {xonshrc_path}\n\n")

        # Load xoncc
        f.write("# Load xoncc\n")
        f.write("import sys\n")
        f.write(f"sys.path.insert(0, '{Path(__file__).parent.parent}')\n")
        f.write("try:\n")
        f.write("    xontrib load xoncc\n")
        f.write("except Exception as e:\n")
        f.write("    print(f'Warning: Failed to load xoncc: {e}')\n")

    try:
        # Launch xonsh with our custom rc file
        env = os.environ.copy()
        env["XONSHRC"] = temp_rc

        # Run xonsh
        try:
            result = subprocess.run(["xonsh"], env=env)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            # Let xonsh handle Ctrl-C naturally
            pass

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_rc)
        except Exception:
            pass


def set_as_default_shell():
    """Helper to set xoncc as default shell."""
    print("To set xoncc as your default shell:")
    print()
    print("1. First, ensure xoncc is in your PATH after installation:")
    print("   $ which xoncc")
    print()
    print("2. Add xoncc to /etc/shells:")
    print("   $ echo $(which xoncc) | sudo tee -a /etc/shells")
    print()
    print("3. Change your default shell:")
    print("   $ chsh -s $(which xoncc)")
    print()
    print("Note: You may need to log out and back in for changes to take effect.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--set-default":
        set_as_default_shell()
    else:
        main()
