# SMPL Avatar Integration

This directory contains the SMPL (Skinned Multi-Person Linear) model integration based on [sxyu/avatar](https://github.com/sxyu/avatar).

## About SMPL Integration

The SMPL integration enhances avatar animation by:

1. Improving motion paths with biomechanically plausible movements
2. Analyzing text prompts to adjust animation parameters
3. Adding subtle physics-based movement enhancements

## Setup

To use SMPL features:

1. Run the setup script: `./scripts/setup_smpl.py`
2. Register and download model files from https://smpl.is.tue.mpg.de/
3. Place the model files in `app/models/smpl/`

## Usage

The SMPL integration works automatically when generating videos. The system will:

- Analyze the text prompt to adjust animation parameters
- Use body pose information to create more realistic movements
- Apply physics-based animation enhancements

No changes to the frontend are required - all enhancements happen behind the scenes.
