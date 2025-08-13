# AI Avatar Video Integrations

This directory contains integrations with external AI repositories to enhance the capabilities of the AI Avatar Video Generator.

## Integrated Repositories

1. **FaceChain** - Identity-preserved portrait generation
   - GitHub: https://github.com/modelscope/facechain.git
   - Used for: Enhancing character portraits

2. **Talking Face Avatar** - Animated talking heads from still images
   - GitHub: https://github.com/Yazdi9/Talking_Face_Avatar.git
   - Used for: Generating talking videos from character images

3. **ComfyUI** - Advanced AI workflows
   - GitHub: https://github.com/comfyanonymous/ComfyUI.git
   - Used for: Advanced image generation and animations

4. **Fast Stable Diffusion** - Optimized diffusion models
   - GitHub: https://github.com/TheLastBen/fast-stable-diffusion.git
   - Used for: High-quality background generation

5. **Avatar3D** - 3D avatar generation
   - GitHub: https://github.com/sxyu/avatar.git
   - Used for: Creating 3D avatars from character images

## Setup Instructions

1. Ensure all prerequisites are installed:
   - Python 3.8 or higher
   - CUDA-compatible GPU (recommended)
   - Git

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Start the integrated services:
   ```bash
   ./start.sh
   ```

4. Stop the services when done:
   ```bash
   ./stop.sh
   ```

## Configuration

The integration services are configured in `config.sh`. You can modify port numbers and other settings there.

## Usage

The integration services are automatically used by the main AI Avatar Video application when available. No additional configuration is needed in the frontend.

## Shared Models

To avoid duplication, models are shared between the integrated repositories through symbolic links. The main model directory is located at `/home/beats/ai-avatar-video/app/models`.
