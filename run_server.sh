#!/usr/bin/env bash

# Direct run script for AI Avatar Video application
set -e

# Use explicit port - no automatic detection
PORT=${1:-8081}
echo "Using explicit port: ${PORT}"

# Set up environment variables
export PORT="${PORT}"
export PYTHONPATH=$(pwd)
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export GUNICORN_BIND="0.0.0.0:${PORT}"
export LOG_LEVEL="INFO"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if we need to run in dev mode
if [ "$2" == "--dev" ]; then
    echo "Starting server in development mode..."
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
else
    # Use direct gunicorn command with bind parameter
    echo "Starting server in production mode with timeout 300 seconds..."
    gunicorn app.main:app \
        --bind "0.0.0.0:${PORT}" \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers 2 \
        --timeout 300
fi
