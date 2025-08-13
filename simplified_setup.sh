#!/usr/bin/env bash

# Simplified setup script for AI Avatar Video application
set -e

echo "Setting up AI Avatar Video application with a simplified approach..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Clean up any existing installations that might cause conflicts
echo "Cleaning up existing installations..."
pip uninstall -y torch torchvision diffusers transformers accelerate

# Install core dependencies first
echo "Installing core dependencies..."
pip install fastapi==0.111.0
pip install "uvicorn[standard]==0.30.1"
pip install "python-multipart>=0.0.7"
pip install "pydantic>=2.0.1,<3.0.0"
pip install gunicorn==21.2.0
pip install SQLAlchemy==2.0.30
pip install aiofiles==22.1.0
pip install requests==2.32.3

# Install image processing dependencies
echo "Installing image processing dependencies..."
pip install pillow==10.3.0
pip install numpy==1.26.4
pip install opencv-python-headless==4.10.0.84
pip install ffmpeg-python==0.2.0
pip install rembg==2.0.56

# Install PyTorch with the specific version
echo "Installing PyTorch..."
pip install torch==2.0.1

# Install diffusers stack with compatible versions
echo "Installing AI dependencies with compatible versions..."
pip install huggingface-hub==0.17.3
pip install tokenizers==0.14.0
pip install transformers==4.34.0
pip install diffusers==0.21.4
pip install accelerate==0.23.0

# Install integration dependencies
echo "Installing integration dependencies..."
pip install tqdm psutil

# Create necessary directories
mkdir -p app/storage/characters app/storage/renders app/storage/thumbs app/static

# Set up environment variables
export PYTHONPATH=$(pwd)
export PORT=8090  # Use a different port entirely
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true

echo "Using port: ${PORT}"

# Start server in development mode
echo "Starting server in development mode..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --reload
