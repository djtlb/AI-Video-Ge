#!/bin/bash

# AI Avatar Video Integration Setup Script
# This script sets up all the integrated repositories and their dependencies

set -e  # Exit on error

# Source the configuration file
source "$(dirname "$0")/config.sh"

echo "========== Setting up AI Avatar Video Integrations =========="
echo "This will install dependencies for all integrated repositories."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y ffmpeg libsm6 libxext6 libgl1 python3-pip python3-venv

# Create a virtual environment for the integrations if it doesn't exist
if [ ! -d "${INTEGRATIONS_DIR}/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${INTEGRATIONS_DIR}/venv"
fi

# Activate the virtual environment
source "${INTEGRATIONS_DIR}/venv/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install common dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install numpy pillow opencv-python-headless fastapi uvicorn pydantic python-multipart aiofiles

# Setup FaceChain
echo "Setting up FaceChain..."
cd "${INTEGRATIONS_DIR}/facechain"
pip install -r requirements.txt
pip install modelscope

# Setup Talking Face Avatar
echo "Setting up Talking Face Avatar..."
cd "${INTEGRATIONS_DIR}/Talking_Face_Avatar"
pip install -r requirements.txt
bash scripts/download_models.sh

# Setup ComfyUI
echo "Setting up ComfyUI..."
cd "${INTEGRATIONS_DIR}/ComfyUI"
pip install -r requirements.txt

# Create symbolic links for shared models to avoid duplication
echo "Setting up shared model directories..."
for dir in "checkpoints" "vae" "lora" "controlnet"; do
    if [ -d "${SHARED_MODELS_DIR}/${dir}" ]; then
        # Create symbolic links in FaceChain
        if [ -d "${FACECHAIN_MODELS_DIR}" ]; then
            ln -sf "${SHARED_MODELS_DIR}/${dir}" "${FACECHAIN_MODELS_DIR}/${dir}"
        fi
        
        # Create symbolic links in ComfyUI
        if [ -d "${COMFYUI_MODELS_DIR}" ]; then
            ln -sf "${SHARED_MODELS_DIR}/${dir}" "${COMFYUI_MODELS_DIR}/${dir}"
        fi
    fi
done

# Create integration-specific .env files
echo "Creating environment configuration files..."

# FaceChain .env
cat > "${INTEGRATIONS_DIR}/facechain/.env" << EOF
PORT=${FACECHAIN_PORT}
ALLOW_ORIGINS=${CORS_ALLOW_ORIGINS}
MODEL_DIR=${FACECHAIN_MODELS_DIR}
EOF

# Talking Face Avatar .env
cat > "${INTEGRATIONS_DIR}/Talking_Face_Avatar/.env" << EOF
PORT=${TALKING_FACE_PORT}
ALLOW_ORIGINS=${CORS_ALLOW_ORIGINS}
MODEL_DIR=${TALKING_FACE_MODELS_DIR}
EOF

# ComfyUI .env
cat > "${INTEGRATIONS_DIR}/ComfyUI/.env" << EOF
PORT=${COMFYUI_PORT}
ALLOW_ORIGINS=${CORS_ALLOW_ORIGINS}
MODEL_DIR=${COMFYUI_MODELS_DIR}
EOF

echo "Setup complete! You can now start the integration services."
echo "To activate the environment, run: source ${INTEGRATIONS_DIR}/venv/bin/activate"
