#!/bin/bash
# Start the Microservice Health Rule Engine demo.
# Usage: ./start.sh [ -b | --background ]

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.dashboard.pid"
PYTHON="$SCRIPT_DIR/.venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
SETUP_DIR="$(dirname "$SCRIPT_DIR")"

if [[ ! -x "$PYTHON" ]]; then
    echo "Virtual environment not found. Run setup.sh first: $SETUP_DIR/setup.sh"
    exit 1
fi
if [[ ! -f "$MAIN_SCRIPT" ]]; then
    echo "main.py not found. Run setup.sh first: $SETUP_DIR/setup.sh"
    exit 1
fi

run_foreground() {
    cd "$SCRIPT_DIR" && "$PYTHON" "$MAIN_SCRIPT"
}

run_background() {
    cd "$SCRIPT_DIR" && nohup "$PYTHON" "$MAIN_SCRIPT" >> "$SCRIPT_DIR/dashboard.log" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Started in background. PID: $(cat "$PID_FILE"). Log: $SCRIPT_DIR/dashboard.log"
    echo "Stop with: ./stop.sh or $SCRIPT_DIR/stop.sh"
}

case "${1:-}" in
    -b|--background)
        run_background
        ;;
    *)
        run_foreground
        ;;
esac
