#!/bin/bash
# Start dashboard. Run from day2/python_launchpad_day2/ or day2/ (via ./start.sh).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
cd "$SRC_DIR" || exit 1
if command -v lsof &>/dev/null; then
  if lsof -ti:5000 &>/dev/null; then
    echo "Dashboard already running on port 5000. Skipping duplicate start."
    exit 0
  fi
elif command -v ss &>/dev/null && ss -tlnp 2>/dev/null | grep -q ':5000 '; then
  echo "Port 5000 already in use. Skipping duplicate start."
  exit 0
fi
# Prefer venv from day2 root
if [ -f "${SCRIPT_DIR}/../.venv/bin/activate" ]; then
  source "${SCRIPT_DIR}/../.venv/bin/activate"
fi
PYTHON_CMD="python"
command -v python &>/dev/null || PYTHON_CMD="python3"
exec $PYTHON_CMD dashboard.py
