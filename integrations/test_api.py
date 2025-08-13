#!/usr/bin/env python
"""
Test script for AI Avatar Video Integrations API

This script tests the connections to the integrated services and
verifies that the API is working correctly.
"""

import os
import sys
import time
import logging
import argparse
import requests
from PIL import Image

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_integrations_status():
    """Test the integrations status endpoint"""
    logger.info("Testing integrations status endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/integrations/status")
        if response.status_code == 200:
            status = response.json()
            logger.info(f"Integrations status: {status}")
            return True
        else:
            logger.error(f"Failed to get integrations status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing integrations status: {e}")
        return False

def test_enhance_portrait():
    """Test the enhance portrait endpoint"""
    logger.info("Testing enhance portrait endpoint...")
    
    # Use a test image
    test_image_path = os.path.join(parent_dir, "app", "static", "test_image.jpg")
    
    # If the test image doesn't exist, create a simple one
    if not os.path.exists(test_image_path):
        logger.info(f"Creating test image at {test_image_path}")
        img = Image.new('RGB', (512, 512), color='white')
        img.save(test_image_path)
    
    # Get the first character from the database
    try:
        response = requests.get("http://localhost:8000/characters")
        if response.status_code == 200:
            characters = response.json()
            if characters:
                char_id = characters[0]["id"]
                logger.info(f"Using character ID {char_id} for testing")
                
                # Test enhance portrait
                data = {
                    "prompt": "high quality portrait"
                }
                
                response = requests.post(
                    f"http://localhost:8000/integrations/enhance-portrait",
                    json={"char_id": char_id, "prompt": data["prompt"]}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Enhance portrait result: {result}")
                    return True
                else:
                    logger.error(f"Failed to enhance portrait: {response.status_code} - {response.text}")
                    return False
            else:
                logger.error("No characters found in the database")
                return False
        else:
            logger.error(f"Failed to get characters: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing enhance portrait: {e}")
        return False

def test_talking_avatar():
    """Test the talking avatar endpoint"""
    logger.info("Testing talking avatar endpoint...")
    
    # Get the first character from the database
    try:
        response = requests.get("http://localhost:8000/characters")
        if response.status_code == 200:
            characters = response.json()
            if characters:
                char_id = characters[0]["id"]
                logger.info(f"Using character ID {char_id} for testing")
                
                # Test talking avatar
                data = {
                    "text": "Hello, this is a test of the talking avatar feature.",
                    "duration_seconds": 5,
                    "use_advanced_motion": True
                }
                
                response = requests.post(
                    f"http://localhost:8000/integrations/generate-talking-avatar",
                    json={"char_id": char_id, **data}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Talking avatar result: {result}")
                    return True
                else:
                    logger.error(f"Failed to generate talking avatar: {response.status_code} - {response.text}")
                    return False
            else:
                logger.error("No characters found in the database")
                return False
        else:
            logger.error(f"Failed to get characters: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing talking avatar: {e}")
        return False

def test_advanced_video():
    """Test the advanced video endpoint"""
    logger.info("Testing advanced video endpoint...")
    
    # Get the first character from the database
    try:
        response = requests.get("http://localhost:8000/characters")
        if response.status_code == 200:
            characters = response.json()
            if characters:
                char_id = characters[0]["id"]
                logger.info(f"Using character ID {char_id} for testing")
                
                # Test advanced video
                data = {
                    "prompt": "A beautiful sunset over the ocean",
                    "character_ids": [char_id],
                    "duration_seconds": 5,
                    "width": 512,
                    "height": 512,
                    "fps": 24,
                    "use_comfyui": True,
                    "use_stable_diffusion": False
                }
                
                response = requests.post(
                    f"http://localhost:8000/integrations/generate-advanced-video",
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Advanced video result: {result}")
                    return True
                else:
                    logger.error(f"Failed to generate advanced video: {response.status_code} - {response.text}")
                    return False
            else:
                logger.error("No characters found in the database")
                return False
        else:
            logger.error(f"Failed to get characters: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing advanced video: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test AI Avatar Video Integrations API")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--status", action="store_true", help="Test integrations status")
    parser.add_argument("--portrait", action="store_true", help="Test enhance portrait")
    parser.add_argument("--talking", action="store_true", help="Test talking avatar")
    parser.add_argument("--video", action="store_true", help="Test advanced video")
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all tests
    if not any(vars(args).values()):
        args.all = True
    
    # Run the tests
    results = {}
    
    if args.all or args.status:
        results["status"] = test_integrations_status()
    
    if args.all or args.portrait:
        results["portrait"] = test_enhance_portrait()
    
    if args.all or args.talking:
        results["talking"] = test_talking_avatar()
    
    if args.all or args.video:
        results["video"] = test_advanced_video()
    
    # Print the results
    logger.info("\n--- Test Results ---")
    for test, result in results.items():
        logger.info(f"{test}: {'PASS' if result else 'FAIL'}")

if __name__ == "__main__":
    main()
