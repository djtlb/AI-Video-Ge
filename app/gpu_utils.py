import os
import json
import subprocess
from typing import Dict, Any
import platform
import psutil

def get_system_info() -> Dict[str, Any]:
    """Get system information including CPU, memory, OS and GPU"""
    info = {
        "cpu": platform.processor() or "Unknown CPU",
        "memory": f"{round(psutil.virtual_memory().total / (1024**3))} GB",
        "os": f"{platform.system()} {platform.release()}",
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
                    ["lspci"], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if "VGA" in line or "Display" in line:
                            if "AMD" in line or "ATI" in line:
                                info["gpu"] = line.split(':')[-1].strip()
                                info["gpu_type"] = "amd"
                            elif "NVIDIA" in line:
                                info["gpu"] = line.split(':')[-1].strip()
                                info["gpu_type"] = "nvidia"
                            elif "Intel" in line:
                                info["gpu"] = line.split(':')[-1].strip()
                                info["gpu_type"] = "intel"
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error detecting GPU: {e}")
    
    return info

def get_gpu_status() -> Dict[str, Any]:
    """Get detailed GPU status specifically for AMD GPUs"""
    status = {
        "gpu_available": False,
        "amd_gpu_available": False,
        "gpu_model": "None detected",
        "gpu_memory": "0 GB",
        "gpu_type": None
    }
    
    # Try to detect AMD GPU
    try:
        # Check for ROCm/AMD GPU
        result = subprocess.run(
            ["rocm-smi", "--showproductname", "--showmeminfo", "vram", "--json"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            gpu_info = json.loads(result.stdout)
            for card, data in gpu_info.items():
                if "GPU Product Name" in data:
                    status["gpu_available"] = True
                    status["amd_gpu_available"] = True
                    status["gpu_model"] = data["GPU Product Name"]
                    status["gpu_type"] = "amd"
                    
                    # Extract memory info
                    if "GPU Memory" in data:
                        mem_info = data["GPU Memory"]
                        if "VRAM Total" in mem_info:
                            mem_total = mem_info["VRAM Total"]
                            # Convert to GB if it's in bytes
                            if isinstance(mem_total, (int, float)):
                                status["gpu_memory"] = f"{round(mem_total / (1024**3))} GB"
                            else:
                                status["gpu_memory"] = mem_total
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
                status["gpu_available"] = True
                gpu_info = result.stdout.strip().split(',')
                if len(gpu_info) >= 1:
                    status["gpu_model"] = gpu_info[0].strip()
                    status["gpu_type"] = "nvidia"
                    if len(gpu_info) >= 2:
                        status["gpu_memory"] = gpu_info[1].strip()
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error checking GPU status: {e}")
    
    return status
