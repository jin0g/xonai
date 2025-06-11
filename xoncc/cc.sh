#!/bin/bash
# cc command - Debug interface for Claude Code (Shell Script version)
# Reads from stdin and sends to claude with real-time streaming output.

# Check for existing session ID in environment variable
CLAUDE_CMD="claude --print --output-format stream-json --verbose"

if [ -n "$CC_SESSION_ID" ]; then
    CLAUDE_CMD="$CLAUDE_CMD --resume $CC_SESSION_ID"
fi

# Read input from stdin
INPUT=$(cat)

if [ -z "$INPUT" ]; then
    echo "Error: No input provided" >&2
    echo "Usage: echo 'your question' | cc" >&2
    exit 1
fi

# Check if claude command exists
if ! command -v claude >/dev/null 2>&1; then
    echo "Error: 'claude' command not found. Please install Claude CLI." >&2
    exit 1
fi

# Create temporary file for capturing session ID
TEMP_DIR=$(mktemp -d)
SESSION_FILE="$TEMP_DIR/session_output"

# Function to clean up temp files
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Run claude and pipe directly to Python formatter while capturing output
echo "$INPUT" | $CLAUDE_CMD 2>/dev/null | tee "$SESSION_FILE" | python3 -c "
import sys
from xoncc.formatters.realtime import RealtimeClaudeFormatter
formatter = RealtimeClaudeFormatter()
for line in sys.stdin:
    formatter.process_json_line(line.strip())
formatter.finalize_output()
"

# Extract session ID from captured output
SESSION_ID=$(grep -o '"session_id":"[^"]*"' "$SESSION_FILE" 2>/dev/null | head -1 | cut -d'"' -f4)

if [ -n "$SESSION_ID" ]; then
    # Export session ID for future use
    export CC_SESSION_ID="$SESSION_ID"
fi