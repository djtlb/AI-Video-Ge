#!/usr/bin/env bash

# Production server launcher for AI Avatar Video
set -e

echo "Starting AI Avatar Video production server..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$(pwd)
export PORT=${PORT:-8080}
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export GUNICORN_BIND="0.0.0.0:${PORT}"
export USE_GPU=true
export GUNICORN_TIMEOUT=300

echo "Using port: ${PORT}"
echo "AMD GPU preference enabled: ${PREFER_AMD_GPU}"

# Run GPU detection test
echo "Testing GPU detection..."
python test_gpu.py

# Start the production server with Gunicorn
echo "Starting production server with Gunicorn..."
gunicorn -c gunicorn_config.py app.main:app
