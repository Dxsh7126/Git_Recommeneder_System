#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo "Starting GitMatch Fullstack System..."
echo "========================================================"

# Activate virtualenv if present
if [ -f "./venv/bin/activate" ]; then
    source ./venv/bin/activate
fi

# Run backend in background
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Run frontend
cd frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:5173"
wait
