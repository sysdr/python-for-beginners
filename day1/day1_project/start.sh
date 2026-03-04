#!/bin/bash
# Start dashboard. Avoid duplicate services. Run from day1_project directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
if command -v lsof &>/dev/null; then
  if lsof -ti:5000 &>/dev/null; then
    echo "Dashboard already running on port 5000. Skipping duplicate start."
    exit 0
  fi
elif command -v ss &>/dev/null && ss -tlnp 2>/dev/null | grep -q ':5000 '; then
  echo "Port 5000 already in use. Skipping duplicate start."
  exit 0
fi
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi
exec python dashboard.py
