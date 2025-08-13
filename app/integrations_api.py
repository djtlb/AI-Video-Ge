"""
AI Avatar Video Integrations API Adapter

This module provides adapter functions to communicate with the integrated services:
- FaceChain for identity-preserved portrait generation
- Talking Face Avatar for animated talking heads
- ComfyUI for advanced image generation workflows
"""

import os
import sys
import requests
import json
import time
import logging
import base64
from typing import Dict, Any, List, Optional
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load service configurations
INTEGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "integrations")
FACECHAIN_PORT = 8001
TALKING_FACE_PORT = 8002
COMFYUI_PORT = 8003
IMAGE_GENERATOR_PORT = 8004

# Base URLs for services
FACECHAIN_URL = f"http://localhost:{FACECHAIN_PORT}"
TALKING_FACE_URL = f"http://localhost:{TALKING_FACE_PORT}"
COMFYUI_URL = f"http://localhost:{COMFYUI_PORT}"
IMAGE_GENERATOR_URL = f"http://localhost:{IMAGE_GENERATOR_PORT}"

# Define timeouts
REQUEST_TIMEOUT = 30  # seconds

# Ensure the services are available
def check_services_available() -> Dict[str, bool]:
    """Check if all integrated services are available."""
    services = {
        "facechain": False,
        "talking_face": False,
        "comfyui": False,
        "image_generator": False
    }
    
    try:
        response = requests.get(f"{FACECHAIN_URL}/health", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            services["facechain"] = True
    except requests.RequestException:
        pass
    
    try:
        response = requests.get(f"{TALKING_FACE_URL}/health", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            services["talking_face"] = True
    except requests.RequestException:
        pass
    
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            services["comfyui"] = True
    except requests.RequestException:
        pass
    
    try:
        # Just check if the server is running
        response = requests.get(f"{IMAGE_GENERATOR_URL}", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200 or response.status_code == 404:  # Either response means server is running
            services["image_generator"] = True
    except requests.RequestException:
        pass
    
    return services

# FaceChain integration functions
def generate_portrait(image_data: bytes, style_name: str = "portrait", 
                      prompt: Optional[str] = None) -> bytes:
    """
    Generate a portrait using FaceChain's FACT algorithm.
    
    Args:
        image_data: Input face image bytes
        style_name: Style to apply (portrait, anime, etc.)
        prompt: Optional text prompt to guide generation
        
    Returns:
        Generated portrait image bytes
    """
    files = {'image': ('input.jpg', image_data, 'image/jpeg')}
    
    data = {
        'style_name': style_name
    }
    
    if prompt:
        data['prompt'] = prompt
    
    try:
        response = requests.post(
            f"{FACECHAIN_URL}/generate_portrait", 
            files=files,
            data=data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"FaceChain portrait generation failed: {response.text}")
            raise Exception(f"FaceChain portrait generation failed: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"FaceChain service error: {str(e)}")
        raise
        
# Talking Face Avatar integration functions
def generate_talking_avatar(image_data: bytes, audio_data: bytes, 
                            enhance: bool = True) -> bytes:
    """
    Generate a talking face video using the input face and audio.
    
    Args:
        image_data: Input face image bytes
        audio_data: Input audio bytes
        enhance: Whether to apply face enhancement
        
    Returns:
        Generated video bytes
    """
    files = {
        'image': ('input.jpg', image_data, 'image/jpeg'),
        'audio': ('input.wav', audio_data, 'audio/wav')
    }
    
    data = {
        'enhance': 'true' if enhance else 'false'
    }
    
    try:
        response = requests.post(
            f"{TALKING_FACE_URL}/generate", 
            files=files,
            data=data,
            timeout=120  # Longer timeout for video generation
        )
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Talking Face generation failed: {response.text}")
            raise Exception(f"Talking Face generation failed: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Talking Face service error: {str(e)}")
        raise

# ComfyUI integration functions
def run_comfyui_workflow(workflow: Dict[str, Any], 
                        input_images: Optional[List[bytes]] = None) -> bytes:
    """
    Run a ComfyUI workflow and return the generated image.
    
    Args:
        workflow: ComfyUI workflow JSON
        input_images: Optional list of input image bytes
        
    Returns:
        Generated image bytes
    """
    # Prepare the request
    prompt = workflow
    
    # Add input images if provided
    if input_images:
        for i, img_bytes in enumerate(input_images):
            img = Image.open(BytesIO(img_bytes))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Add image to the workflow (format depends on ComfyUI workflow structure)
            # This is a simplification; actual implementation may vary based on workflow
            if "6" not in prompt:
                prompt["6"] = {}
            prompt["6"][f"image_{i}"] = {
                "filename": f"input_{i}.png",
                "data": f"data:image/png;base64,{img_base64}"
            }
    
    try:
        # Queue the prompt
        response = requests.post(
            f"{COMFYUI_URL}/prompt", 
            json={"prompt": prompt},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"ComfyUI workflow submission failed: {response.text}")
            raise Exception(f"ComfyUI workflow submission failed: {response.status_code}")
        
        prompt_id = response.json()["prompt_id"]
        
        # Poll for completion
        while True:
            time.sleep(1.0)
            history_resp = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=REQUEST_TIMEOUT)
            
            if history_resp.status_code == 200:
                history = history_resp.json()
                if prompt_id in history and history[prompt_id].get("status") == "complete":
                    # Get the output image
                    outputs = history[prompt_id]["outputs"]
                    if outputs:
                        # Get the first output image
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                image_data = node_output["images"][0]
                                image_url = f"{COMFYUI_URL}/view?filename={image_data['filename']}&subfolder={image_data.get('subfolder', '')}&type=output"
                                
                                # Download the image
                                img_response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
                                if img_response.status_code == 200:
                                    return img_response.content
                    
                    logger.error("No output images found in ComfyUI workflow result")
                    raise Exception("No output images found in ComfyUI workflow result")
                elif history[prompt_id].get("status") == "error":
                    logger.error(f"ComfyUI workflow execution error: {history[prompt_id].get('error')}")
                    raise Exception(f"ComfyUI workflow execution error: {history[prompt_id].get('error')}")
    except requests.RequestException as e:
        logger.error(f"ComfyUI service error: {str(e)}")
        raise

# Image Generator integration functions
def generate_ai_image(prompt: str, size: str = "medium") -> str:
    """
    Generate an image using OpenAI's DALL-E through the image-generator service.
    
    Args:
        prompt: Text prompt describing the image to generate
        size: Size of the image ('small', 'medium', or 'large')
        
    Returns:
        URL of the generated image
    """
    data = {
        'prompt': prompt,
        'size': size
    }
    
    try:
        response = requests.post(
            f"{IMAGE_GENERATOR_URL}/openai/generateimage", 
            json=data,
            timeout=REQUEST_TIMEOUT * 2  # Longer timeout for image generation
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                return result.get('data', '')
            else:
                logger.error(f"Image generation failed: {result.get('error', 'Unknown error')}")
                raise Exception(f"Image generation failed: {result.get('error', 'Unknown error')}")
        else:
            logger.error(f"Image generator service returned status code: {response.status_code}")
            raise Exception(f"Image generator service error: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Image generator service error: {str(e)}")
        raise

# Main API integration class
class IntegrationsAPI:
    """Main class for interacting with integrated services."""
    
    @staticmethod
    def check_services():
        """Check which services are available."""
        return check_services_available()
    
    @staticmethod
    def generate_portrait(image_data, style_name="portrait", prompt=None):
        """Generate portrait using FaceChain."""
        return generate_portrait(image_data, style_name, prompt)
    
    @staticmethod
    def generate_talking_avatar(image_data, audio_data, enhance=True):
        """Generate talking avatar video."""
        return generate_talking_avatar(image_data, audio_data, enhance)
    
    @staticmethod
    def run_comfyui_workflow(workflow, input_images=None):
        """Run ComfyUI workflow."""
        return run_comfyui_workflow(workflow, input_images)
        
    @staticmethod
    def generate_ai_image(prompt, size="medium"):
        """Generate image using OpenAI."""
        return generate_ai_image(prompt, size)
