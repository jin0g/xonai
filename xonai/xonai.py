#!/usr/bin/env python3
"""xonai - Launch xonsh with xonai extension loaded"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path


def main():
    """Launch xonsh with xonai loaded."""
    # Create temporary xonshrc file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsh', delete=False) as temp_rc:
        temp_path = temp_rc.name
        
        # Load user's existing xonshrc if it exists
        user_xonshrc = Path.home() / '.xonshrc'
        if user_xonshrc.exists():
            temp_rc.write(f'source {user_xonshrc}\n')
        
        # Add xonai loading
        temp_rc.write('xontrib load xonai\n')
    
    try:
        # Launch xonsh with custom rc file
        env = os.environ.copy()
        env['XONSHRC'] = temp_path
        
        # Execute xonsh with any additional arguments
        result = subprocess.run(['xonsh'] + sys.argv[1:], env=env)
        sys.exit(result.returncode)
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except OSError:
            pass


if __name__ == '__main__':
    main()