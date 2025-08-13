#!/usr/bin/env bash

# Production-ready setup script for AI Avatar Video application
set -e

# Function to check if port is available
check_port_available() {
    local port=$1
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost $port >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            return 1 # Port is in use
        else
            return 0 # Port is available
        fi
    elif command -v lsof >/dev/null 2>&1; then
        lsof -i:$port >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            return 1 # Port is in use
        else
            return 0 # Port is available
        fi
    else
        # No tools to check, assume available
        return 0
    fi
}

# Find an available port starting from the provided one
find_available_port() {
    local port=$1
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        check_port_available $port
        if [ $? -eq 0 ]; then
            # Port is available, return it silently (no other output)
            echo "$port"
            return 0
        fi
        # This output won't be captured when using command substitution
        >&2 echo "Port $port is in use, trying next port..."
        port=$((port + 1))
        attempt=$((attempt + 1))
    done
    
    # If we're here, we couldn't find an available port
    >&2 echo "Couldn't find an available port after $max_attempts attempts"
    # Return a fallback port instead of exiting
    echo "8099"
    return 1
}

# Clear pip cache if requested
if [ "$1" == "--clear-cache" ]; then
    echo "Clearing pip cache..."
    pip cache purge
    shift
fi

echo "Setting up AI Avatar Video application..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if we need to reinstall
if [ "$1" == "--force-reinstall" ]; then
    echo "Force reinstalling all dependencies..."
    pip uninstall -y torch torchvision transformers diffusers accelerate huggingface_hub tokenizers safetensors
    shift
fi

# Install dependencies
echo "Installing dependencies with fixed versions..."
# Clear any previous installations to avoid conflicts
echo "Cleaning up previous installations..."
pip uninstall -y torch torchvision transformers diffusers accelerate huggingface_hub tokenizers safetensors || true

# Install base dependencies first
echo "Installing base dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install PyTorch separately with a version known to work
echo "Installing PyTorch with a fixed version..."
pip install torch==2.2.0+cpu torchvision==0.17.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Install AI libraries separately
echo "Installing AI libraries with compatible versions..."
pip install transformers diffusers accelerate huggingface_hub tokenizers safetensors

# Create necessary directories
mkdir -p app/storage/characters app/storage/renders app/storage/thumbs app/static

# Find an available port and set environment variables
default_port=${PORT:-8081}
port_to_use=$(find_available_port $default_port)
export PORT="$port_to_use"
echo "Using port: ${PORT}"

# Set up environment variables
export PYTHONPATH=$(pwd)
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export GUNICORN_BIND="0.0.0.0:${PORT}"

# Fix for file watch limit if using development mode
if [ "$1" == "--dev" ]; then
    # Increase file watch limit for development mode
    echo "Setting higher file watch limit for development mode"
    if [ -f /proc/sys/fs/inotify/max_user_watches ]; then
        current=$(cat /proc/sys/fs/inotify/max_user_watches)
        if [ $current -lt 524288 ]; then
            echo "Current max_user_watches is $current, trying to increase..."
            if [ $(id -u) -eq 0 ]; then
                echo 524288 > /proc/sys/fs/inotify/max_user_watches
                echo 524288 > /proc/sys/fs/inotify/max_user_instances
                echo "Increased watch limit to 524288"
            else
                echo "Warning: Cannot increase watch limit, try running with sudo"
            fi
        fi
    fi

    # Start server in development mode
    echo "Starting server in development mode..."
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
else
    # Start server in production mode
    echo "Starting server in production mode with timeout 300 seconds..."
    gunicorn -c gunicorn_config.py app.main:app --timeout 300
fi
