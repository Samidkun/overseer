#!/usr/bin/env bash
# Overseer — 1-Click Launch Script
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PORT="${PORT:-7788}"
HOST="127.0.0.1"

echo "============================================================"
echo "  Starting Overseer Telemetry Daemon on http://$HOST:$PORT"
echo "============================================================"

if command -v xdg-open >/dev/null 2>&1; then
  (sleep 1.2 && xdg-open "http://$HOST:$PORT" >/dev/null 2>&1) &
fi

exec "$DIR/.venv/bin/python" -m backend.serve --port "$PORT" --host "$HOST"
