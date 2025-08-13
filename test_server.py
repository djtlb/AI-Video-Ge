#!/usr/bin/env python3
"""
Simple test script to verify if the AI Avatar Video server is running.
"""

import os
import sys
import requests
import json
import time
from urllib.parse import urljoin

def main():
    """Main function to test server connectivity"""
    port = os.environ.get("PORT", "8084")  # Default to 8084 which is our current port
    base_url = f"http://localhost:{port}"
    
    print(f"Testing server at {base_url}...")
    
    # Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Server is running. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running at {base_url}")
        return False
    
    # Check API docs
    try:
        response = requests.get(urljoin(base_url, "/api/docs"), timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is available")
        else:
            print(f"❌ API documentation returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing API documentation: {e}")
    
    # Check system info
    try:
        response = requests.get(urljoin(base_url, "/system/info"), timeout=5)
        if response.status_code == 200:
            system_info = response.json()
            print("✅ System info endpoint is available")
            print(f"   CPU: {system_info.get('cpu')}")
            print(f"   Memory: {system_info.get('memory')}")
            print(f"   OS: {system_info.get('os')}")
            print(f"   GPU: {system_info.get('gpu')}")
        else:
            print(f"❌ System info returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing system info: {e}")
    
    # Check GPU status
    try:
        response = requests.get(urljoin(base_url, "/gpu/status"), timeout=5)
        if response.status_code == 200:
            gpu_status = response.json()
            print("✅ GPU status endpoint is available")
            print(f"   GPU Available: {gpu_status.get('gpu_available')}")
            print(f"   AMD GPU Available: {gpu_status.get('amd_gpu_available')}")
            print(f"   GPU Model: {gpu_status.get('gpu_model')}")
        else:
            print(f"❌ GPU status returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing GPU status: {e}")
    
    print("\nServer test completed!")
    return True

if __name__ == "__main__":
    main()
