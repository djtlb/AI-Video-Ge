#!/usr/bin/env python3
"""
Test script to create a character in the AI Avatar Video app
"""
import requests
import sys
import os

# Default server URL
SERVER_URL = "http://localhost:8090"

def main():
    # Get test image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Please provide an image path as the first argument")
        sys.exit(1)
    
    # Ensure the image exists
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        sys.exit(1)
    
    # Create a character
    print(f"Creating character with image: {image_path}")
    
    # Prepare the request
    url = f"{SERVER_URL}/characters"
    files = {'file': open(image_path, 'rb')}
    data = {'name': 'Test Character'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Character created successfully!")
        else:
            print("Failed to create character")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
