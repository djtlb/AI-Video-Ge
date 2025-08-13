#!/bin/bash

# AI Avatar Video Integration Start Script
# This script starts all the integrated services

# Source the configuration file
source "$(dirname "$0")/config.sh"

# Activate the virtual environment
source "${INTEGRATIONS_DIR}/venv/bin/activate"

# Function to start a service
start_service() {
    local name=$1
    local dir=$2
    local command=$3
    local port=$4
    
    echo "Starting $name on port $port..."
    cd "$dir"
    
    # Use nohup to keep the process running after the script exits
    # Redirect output to a log file
    nohup $command > "${INTEGRATIONS_DIR}/logs/${name}.log" 2>&1 &
    
    # Save the PID to a file
    echo $! > "${INTEGRATIONS_DIR}/logs/${name}.pid"
    echo "$name started with PID $!"
}

# Create logs directory if it doesn't exist
mkdir -p "${INTEGRATIONS_DIR}/logs"

# Start FaceChain service
start_service "facechain" "${INTEGRATIONS_DIR}/facechain" \
    "python -m app --port ${FACECHAIN_PORT}" \
    ${FACECHAIN_PORT}

# Start Talking Face Avatar service
start_service "talking_face" "${INTEGRATIONS_DIR}/Talking_Face_Avatar" \
    "python app.py --port ${TALKING_FACE_PORT}" \
    ${TALKING_FACE_PORT}

# Start ComfyUI service
start_service "comfyui" "${INTEGRATIONS_DIR}/ComfyUI" \
    "python main.py --port ${COMFYUI_PORT} --listen" \
    ${COMFYUI_PORT}

# Start Image Generator service (Node.js)
start_service "image_generator" "${INTEGRATIONS_DIR}/image-generator" \
    "npm start" \
    ${IMAGE_GENERATOR_PORT}

echo "All services started! Check the logs directory for output."
echo "Use the stop.sh script to stop all services."
