#!/usr/bin/env bash

# Production setup script for AI Avatar Video application
set -e

echo "Setting up AI Avatar Video application for production..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/storage/characters app/storage/renders app/storage/thumbs app/static

# Find an available port
PORT=8080
for p in {8080..8100}; do
    if ! lsof -i:$p > /dev/null 2>&1; then
        PORT=$p
        break
    fi
done

echo "Using port: ${PORT}"

# Set up environment variables
export PYTHONPATH=$(pwd)
export PORT=$PORT
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export GUNICORN_BIND="0.0.0.0:${PORT}"
export LOG_LEVEL="INFO"

# Update gunicorn_config.py to use the correct port
sed -i "s|bind = os.environ.get(\"GUNICORN_BIND\", \"0.0.0.0:[0-9]*\")|bind = os.environ.get(\"GUNICORN_BIND\", \"0.0.0.0:${PORT}\")|g" gunicorn_config.py

# Start the server
if [ "$1" == "--dev" ]; then
    echo "Starting server in development mode..."
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
else
    echo "Starting server in production mode..."
    gunicorn -c gunicorn_config.py app.main:app
fi
