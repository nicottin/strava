#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Python deps ────────────────────────────────────────────────────────────────
echo "→ Installing Python dependencies..."
uv sync --quiet --project "$ROOT"

# ── Node deps ──────────────────────────────────────────────────────────────────
echo "→ Installing Node dependencies..."
(cd "$ROOT/ui" && npm install --silent)

# ── Launch ─────────────────────────────────────────────────────────────────────
echo ""
echo "Starting Strava Dashboard..."
echo "  API  → http://localhost:8000"
echo "  UI   → http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$API_PID" "$UI_PID" 2>/dev/null
  wait "$API_PID" "$UI_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

(cd "$ROOT/api" && uv run --project "$ROOT" uvicorn main:app --port 8000) &
API_PID=$!

# Wait until the API is accepting connections before starting the UI
echo "Waiting for API..."
until curl -sf http://localhost:8000/api/health > /dev/null 2>&1; do
  sleep 0.3
done

(cd "$ROOT/ui" && npm run dev -- --open) &
UI_PID=$!

wait "$API_PID" "$UI_PID"
