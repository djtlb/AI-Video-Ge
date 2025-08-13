import os
import math
from PIL import Image, ImageEnhance, ImageOps

SAFE_AVATAR_MAX = 1024

def ensure_dirs(base_dir):
    for sub in ['storage', 'storage/characters', 'storage/thumbs', 'storage/renders', 'storage/edited']:
        os.makedirs(os.path.join(base_dir, sub), exist_ok=True)

def save_thumbnail(input_path: str, thumb_path: str, size=(256, 256)):
    img = Image.open(input_path).convert('RGBA')
    img.thumbnail(size)
    img.save(thumb_path)

def clamp_avatar_size(png_path: str):
    img = Image.open(png_path).convert('RGBA')
    w, h = img.size
    scale = min(SAFE_AVATAR_MAX / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img.save(png_path)

def edit_character_image(
    input_path: str, 
    output_path: str, 
    scale: float = 1.0,
    rotate: float = 0.0,
    brightness: float = 1.0,
    contrast: float = 1.0
):
    """Edit a character image with various transformations"""
    img = Image.open(input_path).convert('RGBA')
    
    # Apply transformations
    # Scale
    if scale != 1.0:
        w, h = img.size
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Rotate
    if rotate != 0:
        img = img.rotate(rotate, resample=Image.BICUBIC, expand=True)
    
    # Brightness adjustment
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    
    # Contrast adjustment
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    
    # Save the edited image
    img.save(output_path)
    return output_path
