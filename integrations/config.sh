# AI Avatar Video Integration Configuration

# This file configures the integration of multiple AI technologies
# into the AI Avatar Video application.

# Repositories integrated:
# 1. facechain - https://github.com/modelscope/facechain.git
# 2. fast-stable-diffusion - https://github.com/TheLastBen/fast-stable-diffusion.git
# 3. Talking_Face_Avatar - https://github.com/Yazdi9/Talking_Face_Avatar.git
# 4. ComfyUI - https://github.com/comfyanonymous/ComfyUI.git
# 5. image-generator - https://github.com/TrThaele/image-generator.git

INTEGRATIONS_DIR="/home/beats/ai-avatar-video/integrations"

# Service configuration
FACECHAIN_PORT=8001
TALKING_FACE_PORT=8002
COMFYUI_PORT=8003
IMAGE_GENERATOR_PORT=8004

# CORS settings for all services
CORS_ALLOW_ORIGINS="http://localhost:8000,http://localhost:7860,http://127.0.0.1:8000,http://127.0.0.1:7860"

# Path configurations
FACECHAIN_MODELS_DIR="${INTEGRATIONS_DIR}/facechain/models"
COMFYUI_MODELS_DIR="${INTEGRATIONS_DIR}/ComfyUI/models"
TALKING_FACE_MODELS_DIR="${INTEGRATIONS_DIR}/Talking_Face_Avatar/checkpoints"
IMAGE_GENERATOR_MODELS_DIR="${INTEGRATIONS_DIR}/image-generator/models"

# Shared model directory to avoid duplication
SHARED_MODELS_DIR="/home/beats/ai-avatar-video/app/models"

# Function to check if a path exists
check_path() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo "Created directory: $1"
    fi
}

# Initialize required directories
check_path "$FACECHAIN_MODELS_DIR"
check_path "$COMFYUI_MODELS_DIR"
check_path "$TALKING_FACE_MODELS_DIR"
check_path "$IMAGE_GENERATOR_MODELS_DIR"
check_path "$SHARED_MODELS_DIR"
