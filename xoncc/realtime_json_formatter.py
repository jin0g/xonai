#!/usr/bin/env python3
"""Real-time JSON formatter for Claude streaming output"""

# This module is deprecated. Use xoncc.formatters.realtime instead.
from xoncc.formatters.realtime import RealtimeClaudeFormatter


def main():
    """Main entry point"""
    import sys

    formatter = RealtimeClaudeFormatter()
    formatter.format_stream(sys.stdin)


if __name__ == "__main__":
    main()
