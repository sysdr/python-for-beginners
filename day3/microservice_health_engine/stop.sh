#!/bin/bash
# Stop the Microservice Health Rule Engine demo (when run in background).
# Usage: ./stop.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.dashboard.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo "No PID file found. Nothing to stop."
    echo "Tip: Start in background with: ./start.sh --background"
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    echo "Stopped process $PID."
else
    echo "Process $PID is not running."
fi
rm -f "$PID_FILE"
