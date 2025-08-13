#!/bin/bash

# AI Avatar Video Integration Stop Script
# This script stops all the integrated services

# Source the configuration file
source "$(dirname "$0")/config.sh"

# Function to stop a service
stop_service() {
    local name=$1
    local pid_file="${INTEGRATIONS_DIR}/logs/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        echo "Stopping $name (PID: $pid)..."
        
        # Try graceful termination first
        kill $pid 2>/dev/null || true
        
        # Wait a moment
        sleep 2
        
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo "$name is still running, force killing..."
            kill -9 $pid 2>/dev/null || true
        fi
        
        rm -f "$pid_file"
        echo "$name stopped"
    else
        echo "$name is not running"
    fi
}

# Stop all services
stop_service "facechain"
stop_service "talking_face"
stop_service "comfyui"
stop_service "image_generator"

echo "All services stopped!"
