#!/usr/bin/env python3
"""
Minimal FastAPI server that tests AMD GPU integration
"""

import os
import json
from typing import Dict, Any
import subprocess

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="AMD GPU Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set AMD GPU preference
os.environ["PREFER_AMD_GPU"] = "1"

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple HTML page"""
    return """
    <html>
        <head>
            <title>AMD GPU Test Server</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .info { background-color: #f0f0f0; padding: 15px; border-radius: 5px; }
                .gpu-info { margin-top: 20px; }
                .endpoints { margin-top: 20px; }
                .endpoint { margin: 10px 0; padding: 10px; background-color: #e0e0e0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>AMD GPU Test Server</h1>
            <div class="info">
                <p>This is a minimal server to test AMD GPU integration.</p>
                <p>The server is running and ready to accept requests.</p>
            </div>
            <div class="endpoints">
                <h2>Available Endpoints:</h2>
                <div class="endpoint">
                    <strong>GET /system-info</strong>
                    <p>Returns system information including GPU status</p>
                </div>
                <div class="endpoint">
                    <strong>GET /gpu-status</strong>
                    <p>Returns detailed GPU status with AMD GPU information</p>
                </div>
                <div class="endpoint">
                    <strong>GET /pytorch-info</strong>
                    <p>Returns PyTorch configuration and GPU detection</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/system-info")
async def system_info():
    """Get system information including CPU, memory, OS and GPU"""
    info = {
        "cpu": subprocess.getoutput("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2").strip(),
        "memory": subprocess.getoutput("free -h | awk '/^Mem:/ {print $2}'").strip(),
        "os": subprocess.getoutput("cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2").strip(),
        "gpu": "None detected"
    }
    
    # Try to detect GPU
    try:
        # First try rocm-smi for AMD GPUs
        result = subprocess.run(
            ["rocm-smi", "--showproductname", "--json"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            gpu_info = json.loads(result.stdout)
            for card, data in gpu_info.items():
                if "GPU Product Name" in data:
                    info["gpu"] = data["GPU Product Name"]
                    info["gpu_type"] = "amd"
                    info["gpu_memory"] = data.get("GPU Memory", "Unknown")
                    break
        else:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                gpu_info = result.stdout.strip().split(',')
                if len(gpu_info) >= 1:
                    info["gpu"] = gpu_info[0].strip()
                    info["gpu_type"] = "nvidia"
                    if len(gpu_info) >= 2:
                        info["gpu_memory"] = gpu_info[1].strip()
            else:
                # Try lspci as a fallback
                result = subprocess.run(
                    ["lspci | grep -i vga"], 
                    shell=True,
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.split('\n'):
                        if "AMD" in line or "ATI" in line:
                            info["gpu"] = line.split(':')[-1].strip()
                            info["gpu_type"] = "amd"
                        elif "NVIDIA" in line:
                            info["gpu"] = line.split(':')[-1].strip()
                            info["gpu_type"] = "nvidia"
                        elif "Intel" in line:
                            info["gpu"] = line.split(':')[-1].strip()
                            info["gpu_type"] = "intel"
    except Exception as e:
        info["gpu_error"] = str(e)
    
    return info

@app.get("/gpu-status")
async def gpu_status():
    """Get detailed GPU status specifically for AMD GPUs"""
    status = {
        "gpu_available": False,
        "amd_gpu_available": False,
        "gpu_model": "None detected",
        "gpu_memory": "0 GB",
        "gpu_type": None,
        "commands_output": {}
    }
    
    # Try different commands to detect GPU
    commands = [
        {"name": "rocm-smi", "cmd": "rocm-smi --showproductname"},
        {"name": "nvidia-smi", "cmd": "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"},
        {"name": "lspci-vga", "cmd": "lspci | grep -i vga"},
        {"name": "lspci-3d", "cmd": "lspci | grep -i '3d controller'"}
    ]
    
    for cmd_info in commands:
        try:
            result = subprocess.run(
                cmd_info["cmd"], 
                shell=True,
                capture_output=True, 
                text=True,
                timeout=5
            )
            status["commands_output"][cmd_info["name"]] = {
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
            
            # Check for AMD GPU in output
            if result.returncode == 0 and result.stdout.strip():
                if "AMD" in result.stdout or "ATI" in result.stdout:
                    status["gpu_available"] = True
                    status["amd_gpu_available"] = True
                    status["gpu_type"] = "amd"
                    status["gpu_model"] = result.stdout.strip()
                elif "NVIDIA" in result.stdout:
                    status["gpu_available"] = True
                    status["gpu_type"] = "nvidia"
                    status["gpu_model"] = result.stdout.strip()
        except Exception as e:
            status["commands_output"][cmd_info["name"]] = {
                "error": str(e)
            }
    
    # Additional information from environment
    status["prefer_amd_gpu"] = os.environ.get("PREFER_AMD_GPU", "1") == "1"
    
    return status

@app.get("/pytorch-info")
async def pytorch_info():
    """Get PyTorch configuration and GPU detection"""
    info = {
        "pytorch_available": False,
        "version": None,
        "cuda_available": False,
        "rocm_available": False,
        "device_used": "cpu"
    }
    
    try:
        # Try to import torch
        import torch
        info["pytorch_available"] = True
        info["version"] = torch.__version__
        
        # Check CUDA
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
        
        # Check ROCm
        if hasattr(torch, 'version') and hasattr(torch.version, 'hip'):
            info["rocm_version"] = torch.version.hip
            info["rocm_available"] = torch.version.hip and torch.version.hip != ''
        
        # Determine device based on AMD preference
        prefer_amd = os.environ.get("PREFER_AMD_GPU", "1") == "1"
        
        if prefer_amd and info["rocm_available"]:
            info["device_used"] = "cuda (AMD/ROCm)"
        elif info["cuda_available"]:
            info["device_used"] = "cuda (NVIDIA)"
        elif hasattr(torch, 'has_mps') and torch.has_mps:
            info["device_used"] = "mps (Apple Silicon)"
        else:
            info["device_used"] = "cpu"
        
        # Add tensor test
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        info["device_object"] = str(device)
        
        # Create a small tensor on the device
        x = torch.rand(5, 3)
        x = x.to(device)
        info["tensor_device"] = str(x.device)
        info["tensor_test_passed"] = True
        
    except ImportError as e:
        info["import_error"] = str(e)
    except Exception as e:
        info["error"] = str(e)
    
    return info

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)
