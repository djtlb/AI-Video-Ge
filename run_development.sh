#!/usr/bin/env bash

# Development server launcher for AI Avatar Video
set -e

echo "Starting AI Avatar Video development server..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$(pwd)
export PORT=${PORT:-8090}
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export DEBUG=true

echo "Using port: ${PORT}"
echo "AMD GPU preference enabled: ${PREFER_AMD_GPU}"

# Run GPU detection test
echo "Testing GPU detection..."
python test_gpu.py

# Start the development server with Uvicorn
echo "Starting development server with hot-reload..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
