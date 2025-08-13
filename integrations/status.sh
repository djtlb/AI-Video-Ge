#!/bin/bash
# Check the status of AI Avatar Video integration services

# Source the configuration file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "=========== AI Avatar Video Integration Status ==========="

# Function to check if a service is running
check_service() {
    local name=$1
    local pid_file="${LOGS_DIR}/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "✅ $name is running (PID: $pid)"
            return 0
        else
            echo "❌ $name is not running (stale PID file)"
            return 1
        fi
    else
        echo "❌ $name is not running"
        return 1
    fi
}

# Function to check if a port is in use
check_port() {
    local name=$1
    local port=$2
    
    if netstat -tuln | grep -q ":$port "; then
        echo "✅ Port $port is in use by $name"
        return 0
    else
        echo "❌ Port $port is not in use by $name"
        return 1
    fi
}

# Check repository directories
echo -e "\n--- Repository Status ---"
repo_check() {
    local name=$1
    local dir=$2
    
    if [ -d "$dir" ] && [ -d "$dir/.git" ]; then
        echo "✅ $name repository exists at $dir"
        return 0
    else
        echo "❌ $name repository is missing"
        return 1
    fi
}

repo_check "FaceChain" "$FACECHAIN_DIR"
repo_check "Talking Face Avatar" "$TALKING_FACE_DIR"
repo_check "ComfyUI" "$COMFYUI_DIR"
repo_check "Fast Stable Diffusion" "$STABLE_DIFFUSION_DIR"
repo_check "Avatar3D" "$AVATAR3D_DIR"
repo_check "Image Generator" "$INTEGRATIONS_DIR/image-generator"

# Check service status
echo -e "\n--- Service Status ---"
check_service "facechain"
check_service "talking_face"
check_service "comfyui"
check_service "image_generator"

# Check port usage
echo -e "\n--- Port Status ---"
check_port "FaceChain" "$FACECHAIN_PORT"
check_port "Talking Face Avatar" "$TALKING_FACE_PORT"
check_port "ComfyUI" "$COMFYUI_PORT"
check_port "Image Generator" "$IMAGE_GENERATOR_PORT"

# Check log files
echo -e "\n--- Log Status ---"
for service in "facechain" "talking_face" "comfyui" "image_generator"; do
    log_file="${LOGS_DIR}/${service}.log"
    if [ -f "$log_file" ]; then
        log_size=$(du -h "$log_file" | cut -f1)
        echo "✅ $service log exists (Size: $log_size)"
        echo "   Last 3 lines:"
        tail -n 3 "$log_file" | sed 's/^/   /'
    else
        echo "❌ $service log is missing"
    fi
done

echo -e "\n--- Integration API Status ---"
# Check if the API is accessible from the main app
if curl -s "http://localhost:8000/integrations/status" > /dev/null 2>&1; then
    echo "✅ Integration API is accessible"
    # Show the status from the API
    curl -s "http://localhost:8000/integrations/status" | python -m json.tool
else
    echo "❌ Integration API is not accessible"
fi

echo -e "\nFor more details, check the log files in ${LOGS_DIR}"
