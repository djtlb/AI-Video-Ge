#!/usr/bin/env python3

"""
AMD GPU Detection Test Script
This script checks if an AMD GPU is available and prints its details.
"""

import os
import sys
import torch
import json

def check_gpu():
    """Check for GPUs with priority for AMD GPUs"""
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
        gpu_info["device"] = "cuda"  # PyTorch uses 'cuda' for ROCm too
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

def check_system_hardware():
    """Check system hardware information"""
    import platform
    import psutil
    try:
        import subprocess
        
        info = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu": platform.processor(),
            "memory": f"{round(psutil.virtual_memory().total / (1024**3))} GB",
            "python": sys.version,
            "torch": torch.__version__,
        }
        
        # Try to get GPU info using lspci
        try:
            lspci_output = subprocess.check_output(["lspci"], text=True)
            for line in lspci_output.split('\n'):
                if "VGA" in line or "Display" in line or "3D" in line:
                    if "AMD" in line or "ATI" in line:
                        info["gpu_lspci"] = line.strip()
                        info["gpu_type"] = "AMD"
                    elif "NVIDIA" in line:
                        info["gpu_lspci"] = line.strip()
                        info["gpu_type"] = "NVIDIA"
        except Exception as e:
            info["lspci_error"] = str(e)
            
        # Try rocm-smi for AMD
        try:
            rocm_output = subprocess.check_output(["rocm-smi"], text=True)
            info["rocm_smi"] = rocm_output
        except Exception as e:
            info["rocm_smi_error"] = str(e)
            
        # Try nvidia-smi for NVIDIA
        try:
            nvidia_output = subprocess.check_output(["nvidia-smi"], text=True)
            info["nvidia_smi"] = nvidia_output
        except Exception as e:
            info["nvidia_smi_error"] = str(e)
            
        return info
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Print environment variables
    print("Environment variables:")
    print(f"PREFER_AMD_GPU: {os.environ.get('PREFER_AMD_GPU', 'Not set')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"PORT: {os.environ.get('PORT', 'Not set')}")
    print()
    
    # Check GPU
    print("GPU Information:")
    gpu_info = check_gpu()
    print(json.dumps(gpu_info, indent=2))
    print()
    
    # Check system hardware
    print("System Hardware Information:")
    system_info = check_system_hardware()
    print(json.dumps(system_info, indent=2))
    
    # Summary
    print("\nSummary:")
    print(f"Using: {gpu_info.get('using', 'Unknown')}")
    print(f"Device: {gpu_info.get('device', 'Unknown')}")
    if gpu_info.get("amd_rocm_available"):
        print("AMD GPU is available and will be used!")
    elif gpu_info.get("nvidia_cuda_available"):
        print("NVIDIA GPU is available and will be used!")
    elif gpu_info.get("apple_mps_available"):
        print("Apple Silicon GPU is available and will be used!")
    else:
        print("No GPU available, using CPU.")
    
    # Check if preferred AMD GPU is available
    if os.environ.get("PREFER_AMD_GPU", "true").lower() == "true" and not gpu_info.get("amd_rocm_available"):
        print("\nWarning: AMD GPU is preferred but not available.")
        print("To use NVIDIA GPU instead, set PREFER_AMD_GPU=false")
    
    print("\nDone!")
