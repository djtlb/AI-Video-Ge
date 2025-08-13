#!/usr/bin/env bash

# Simple setup script for AI Avatar Video application
set -e

echo "Setting up AI Avatar Video application with simplified approach..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Clear any previous installations to avoid conflicts
echo "Cleaning up previous installations..."
pip uninstall -y torch torchvision transformers diffusers accelerate huggingface_hub tokenizers safetensors || true

# Install base dependencies first
echo "Installing base dependencies..."
pip install --upgrade pip setuptools wheel

# Install core dependencies without ML libraries
echo "Installing core FastAPI dependencies..."
pip install "fastapi>=0.100.0" "uvicorn[standard]>=0.20.0" "pydantic>=2.0.0,<3.0.0" "python-multipart>=0.0.7"
pip install "gunicorn>=21.0.0" "SQLAlchemy>=2.0.0" "aiofiles>=22.0.0" "requests>=2.25.0"
pip install "ffmpeg-python>=0.2.0" "pillow>=10.0.0" "numpy>=1.20.0" "opencv-python-headless>=4.0.0"
pip install "rembg>=2.0.0" "tqdm>=4.0.0" "psutil>=5.0.0"

# Install PyTorch separately
echo "Installing PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install diffusers stack
echo "Installing AI dependencies with compatible versions..."
pip install transformers diffusers accelerate safetensors huggingface_hub tokenizers

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

# Set up environment variables
export PYTHONPATH=$(pwd)
export PORT=$PORT
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:${PORT},http://127.0.0.1:3000,http://127.0.0.1:${PORT}"
export PREFER_AMD_GPU=true
export GUNICORN_BIND="0.0.0.0:${PORT}"
export LOG_LEVEL="INFO"

echo "Using port: ${PORT}"

# Create minimal test server if it doesn't exist
if [ ! -f "minimal_server.py" ]; then
cat > minimal_server.py << 'EOF'
import os
import sys
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI(title="AI Avatar Video - Minimal Test Server")

@app.get("/")
def root():
    return {"message": "AI Avatar Video Minimal Test Server Running"}

@app.get("/gpu/info")
def gpu_info():
    """Test GPU detection"""
    try:
        import torch
        gpu_info = {
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "prefer_amd": os.environ.get("PREFER_AMD_GPU", "true").lower() == "true",
        }
        
        # Check for AMD GPU (ROCm)
        if hasattr(torch, "version") and hasattr(torch.version, "hip") and torch.version.hip != "":
            gpu_info["amd_rocm_available"] = True
            gpu_info["rocm_version"] = torch.version.hip
            gpu_info["device"] = "cuda" # PyTorch uses 'cuda' for ROCm too
            gpu_info["using"] = "AMD GPU with ROCm"
        else:
            gpu_info["amd_rocm_available"] = False
            
        # Check for NVIDIA GPU
        if torch.cuda.is_available():
            gpu_info["nvidia_cuda_available"] = True
            gpu_info["cuda_version"] = torch.version.cuda
            for i in range(torch.cuda.device_count()):
                gpu_info[f"device_{i}_name"] = torch.cuda.get_device_name(i)
            gpu_info["device"] = "cuda"
            if not gpu_info.get("using"):
                gpu_info["using"] = "NVIDIA GPU with CUDA"
                
        # Check for Apple Silicon
        if hasattr(torch, "has_mps") and torch.has_mps:
            gpu_info["apple_mps_available"] = True
            gpu_info["device"] = "mps"
            if not gpu_info.get("using"):
                gpu_info["using"] = "Apple Silicon GPU with MPS"
        else:
            gpu_info["apple_mps_available"] = False
            
        # If no GPU is available
        if not gpu_info.get("using"):
            gpu_info["using"] = "CPU (no GPU detected)"
            gpu_info["device"] = "cpu"
            
        return gpu_info
    except Exception as e:
        return {"error": str(e), "using": "CPU (error detecting GPU)"}

@app.get("/system/info")
def system_info():
    """Get system information"""
    import platform
    import psutil
    
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "python": sys.version,
        "cpu": platform.processor(),
        "memory": f"{round(psutil.virtual_memory().total / (1024**3))} GB",
        "environment": {
            "PORT": os.environ.get("PORT", "8080"),
            "PREFER_AMD_GPU": os.environ.get("PREFER_AMD_GPU", "true"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        }
    }
    return info

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
    echo "Created minimal test server"
fi

# Make the script executable
chmod +x minimal_server.py

echo "Setup complete! Starting minimal test server on port ${PORT}..."
echo "Access the server at http://localhost:${PORT}"
echo "Check GPU status at http://localhost:${PORT}/gpu/info"
echo "Check system info at http://localhost:${PORT}/system/info"

python minimal_server.py
