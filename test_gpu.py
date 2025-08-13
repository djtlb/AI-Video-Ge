#!/usr/bin/env python3
"""
Simple script to test AMD GPU detection and PyTorch setup
"""

import os
import sys

def main():
    """Test AMD GPU detection and PyTorch setup"""
    print("Testing AMD GPU detection and PyTorch setup...")
    
    # Set environment variable to prefer AMD GPU
    os.environ["PREFER_AMD_GPU"] = "1"
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        
        # Check if CUDA is available
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        
        # Check for AMD GPU via ROCm
        if hasattr(torch, 'version') and hasattr(torch.version, 'hip'):
            print(f"ROCm/HIP version: {torch.version.hip}")
            if torch.version.hip and torch.version.hip != '':
                print("AMD GPU detected with ROCm support!")
                # Use 'cuda' device for AMD with ROCm
                device = torch.device('cuda')
                print(f"Using device: {device}")
                
                # Create a small tensor and move it to GPU to test
                x = torch.rand(5, 3)
                x = x.to(device)
                print(f"Test tensor device: {x.device}")
                print("AMD GPU is working correctly!")
            else:
                print("No AMD GPU with ROCm detected")
        else:
            print("PyTorch was not built with ROCm/HIP support")
        
        # Print device priority
        print("\nDevice priority check:")
        device = 'cpu'
        if hasattr(torch, 'version') and hasattr(torch.version, 'hip') and torch.version.hip and torch.version.hip != '':
            device = 'cuda'  # ROCm/AMD, PyTorch uses 'cuda' for ROCm
            print("Priority 1: Using AMD GPU with ROCm (device='cuda')")
        elif torch.cuda.is_available():
            device = 'cuda'
            print("Priority 2: Using NVIDIA GPU with CUDA")
        elif hasattr(torch, 'has_mps') and torch.has_mps:
            device = 'mps'
            print("Priority 3: Using Apple Silicon GPU with MPS")
        else:
            print("Fallback: Using CPU")
        
        print(f"Selected device: {device}")
        return 0
    
    except ImportError as e:
        print(f"Error importing PyTorch: {e}")
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
