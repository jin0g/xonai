#!/usr/bin/env python3
"""JSON formatter for Claude streaming output"""

# This module is deprecated. Use xoncc.formatters.log instead.
import sys

from xoncc.formatters.log import format_claude_json_stream as _format_claude_json_stream


def format_claude_json_stream(input_stream) -> None:
    """Format Claude JSON stream output to readable text"""
    # Read all lines from stream
    lines = []
    for line in input_stream:
        lines.append(line.strip())

    # Format using the new module
    json_stream = "\n".join(lines)
    formatted = _format_claude_json_stream(json_stream)

    if formatted.strip():
        print(formatted)
    else:
        print("No content extracted from JSON stream")


def main():
    """Main entry point"""
    try:
        format_claude_json_stream(sys.stdin)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error formatting Claude output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
