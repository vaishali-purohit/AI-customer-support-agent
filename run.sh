#!/bin/bash

set -m  # monitor mode: background jobs get separate process groups

BACKEND_PGID=""
FRONTEND_PGID=""

cleanup() {
    echo ""
    echo "→ Stopping services..."
    [ -n "$BACKEND_PGID" ] && kill -- "-$BACKEND_PGID" 2>/dev/null
    [ -n "$FRONTEND_PGID" ] && kill -- "-$FRONTEND_PGID" 2>/dev/null
    wait 2>/dev/null
    echo "✓ Stopped."
    exit 0
}

trap cleanup INT TERM

(cd backend && ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PGID=$!
(cd frontend && npm run dev) &
FRONTEND_PGID=$!

wait
