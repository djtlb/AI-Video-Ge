#!/usr/bin/env python3
"""
Script to create a new character using the REST API
"""
import requests
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Create a new character')
    parser.add_argument('--name', required=True, help='Name of the character')
    parser.add_argument('--image', required=True, help='Path to the image file')
    parser.add_argument('--url', default='http://localhost:8084', help='URL of the server')
    
    args = parser.parse_args()
    
    # Validate image path
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)
    
    # Prepare the request
    url = f"{args.url}/characters"
    files = {'file': open(args.image, 'rb')}
    data = {'name': args.name}
    
    try:
        print(f"Creating character '{args.name}' with image: {args.image}")
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            print("Character created successfully!")
            print(response.json())
        else:
            print(f"Failed to create character. Status code: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
