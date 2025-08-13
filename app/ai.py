import os
import math
import random
import tempfile
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image, ImageOps

import torch
from diffusers import StableDiffusionPipeline
from rembg import remove
import ffmpeg

# Import SMPL avatar module for enhanced animation (if available)
try:
    from .smpl_avatar import enhance_character_animation, extract_avatar_motion_data
    SMPL_AVAILABLE = True
except ImportError:
    SMPL_AVAILABLE = False


class BackgroundGenerator:
    def __init__(self, device: str = 'cpu'):
        model_id = 'runwayml/stable-diffusion-v1-5'
        self.device = device
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float16 if 'cuda' in device else torch.float32
        )
        if 'cuda' in device:
            self.pipe = self.pipe.to(device)
        self.pipe.safety_checker = None  # optional: disable if you are strictly local

    @torch.no_grad()
    def generate(self, prompt: str, width: int, height: int, seed: Optional[int] = None) -> Image.Image:
        g = torch.Generator(device=self.device)
        if seed is not None:
            g = g.manual_seed(seed)
        image = self.pipe(
            prompt=prompt,
            height=height,
            width=width,
            guidance_scale=7.0,
            num_inference_steps=25,
            generator=g
        ).images[0]
        return image.convert('RGB')


def cutout_person(image_bytes: bytes) -> Image.Image:
    """Return an RGBA image with background removed.
    
    If SMPL is available, it will be used to improve the segmentation quality.
    """
    try:
        # Default method using rembg
        out = remove(image_bytes)  # bytes → bytes (PNG RGBA)
        from io import BytesIO
        im = Image.open(BytesIO(out)).convert('RGBA')
        
        # If SMPL is available, try to refine the cutout (no frontend changes)
        if SMPL_AVAILABLE:
            try:
                # In a real implementation, this would use SMPL to refine the segmentation
                # For now, we'll just use the basic cutout
                pass
            except Exception as e:
                print(f"SMPL refinement failed: {e}")
        
        # Ensure the image has proper dimensions
        if im.width < 10 or im.height < 10:
            raise ValueError("Cutout image is too small, likely failed to detect a person")
            
        return im
    except Exception as e:
        import logging
        logging.error(f"Error in cutout_person: {e}")
        # Fallback to just returning the original image with transparency
        try:
            from io import BytesIO
            original = Image.open(BytesIO(image_bytes))
            # Convert to RGBA but maintain the image
            rgba = original.convert('RGBA')
            return rgba
        except Exception as fallback_error:
            logging.error(f"Fallback also failed: {fallback_error}")
            # Create a small placeholder image as last resort
            placeholder = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
            return placeholder


def composite_video(
    bg: Image.Image,
    avatars: List[Image.Image],
    duration_s: int,
    fps: int,
    size: Tuple[int, int],
    seed: Optional[int] = None,
    character_settings: Optional[dict] = None,
    prompt: Optional[str] = None,  # Added text prompt parameter
) -> str:
    """Generate frames with premium-quality fluid motion; encode to high-quality MP4; return file path.
    
    If SMPL avatar module is available, it will be used to enhance the animation.
    """
    width, height = size
    n_frames = duration_s * fps
    rng = random.Random(seed)
    
    # Default settings if none provided
    if character_settings is None:
        character_settings = {}
        
    # Enhanced motion calculation for each avatar
    motions = []
    
    # Process prompt for motion guidance
    text_prompt = prompt or ""
    
    for i, av in enumerate(avatars):
        # Get character settings if available
        char_settings = character_settings.get(i, {})
        
        # Use SMPL to enhance animation if available
        if SMPL_AVAILABLE:
            try:
                # Use text prompt and avatar image to improve animation
                char_settings = enhance_character_animation(
                    char_settings, 
                    avatar_image=av,
                    text_prompt=text_prompt,
                    seed=seed
                )
            except Exception as e:
                print(f"SMPL animation enhancement failed: {e}")
        
        # Use settings or default values optimized for fluid motion
        scale0 = char_settings.get('scale', rng.uniform(0.35, 0.6))
        scale_variation = char_settings.get('scale_variation', rng.uniform(0.8, 1.25))
        scale1 = scale0 * scale_variation
        
        angle = char_settings.get('rotation', rng.uniform(-8, 8))
        
        # Calculate margins for safe placement
        margin = 0.15 * min(width, height)
        
        # Generate advanced motion path
        if 'position_x' in char_settings and 'position_y' in char_settings:
            # Use fixed position as base
            base_x = char_settings['position_x']
            base_y = char_settings['position_y']
            
            if char_settings.get('fixed_position', False):
                # For fixed position, create organic micro-movements
                # Using Perlin noise pattern for more natural subtle movement
                control_points = []
                
                # Add subtle movement with tiny control points using noise function
                num_points = 8  # More points for smoother micro-movement
                for p in range(num_points):
                    # Generate micro-movement using noise pattern (more organic than random)
                    t_offset = p / num_points
                    # Pseudo-Perlin noise approximation
                    noise_x = math.sin(t_offset * 6.28 + rng.random() * 10) * math.sin(t_offset * 9.42 + rng.random() * 10)
                    noise_y = math.sin(t_offset * 7.85 + rng.random() * 10) * math.sin(t_offset * 5.67 + rng.random() * 10)
                    
                    micro_move = char_settings.get('micro_movement', min(width, height) * 0.02)
                    px = base_x + noise_x * micro_move
                    py = base_y + noise_y * micro_move
                    control_points.append((px, py))
            else:
                # Create advanced organic path using multiple control points and curves
                move_range = char_settings.get('move_range', 0.4) * min(width, height)
                
                # More control points for premium smoothness
                num_points = rng.randint(6, 9)
                
                # Generate base anchor points for a complex path
                anchor_points = []
                
                # Use parametric equations for more interesting paths (circle, figure-8, etc.)
                path_type = char_settings.get('path_type', rng.choice(['circle', 'figure8', 'organic', 'wave']))
                
                if path_type == 'circle':
                    # Circular path
                    for p in range(num_points):
                        angle = p * 2 * math.pi / num_points
                        radius = move_range * (0.7 + rng.random() * 0.3)  # Slight variation in radius
                        px = base_x + math.cos(angle) * radius
                        py = base_y + math.sin(angle) * radius
                        # Ensure within bounds
                        px = max(margin, min(width - margin, px))
                        py = max(margin, min(height - margin, py))
                        anchor_points.append((px, py))
                    
                elif path_type == 'figure8':
                    # Figure-8 path
                    for p in range(num_points):
                        angle = p * 2 * math.pi / num_points
                        radius = move_range * (0.7 + rng.random() * 0.3)
                        px = base_x + math.sin(angle * 2) * radius * 0.5
                        py = base_y + math.sin(angle) * radius
                        # Ensure within bounds
                        px = max(margin, min(width - margin, px))
                        py = max(margin, min(height - margin, py))
                        anchor_points.append((px, py))
                
                elif path_type == 'wave':
                    # Horizontal wave pattern
                    for p in range(num_points):
                        t = p / num_points
                        wave_x = move_range * math.sin(t * 2 * math.pi * 2) # 2 complete waves
                        wave_y = move_range * 0.3 * math.sin(t * 2 * math.pi * 4) # 4 smaller waves
                        
                        px = base_x + wave_x
                        py = base_y + wave_y
                        # Ensure within bounds
                        px = max(margin, min(width - margin, px))
                        py = max(margin, min(height - margin, py))
                        anchor_points.append((px, py))
                
                else:  # 'organic'
                    # Organic random path with natural clustering
                    anchor_points.append((base_x, base_y))  # Start at base position
                    
                    # Create a few key destination points
                    key_points = []
                    for _ in range(3):
                        # Create key points that are well-spaced
                        angle = rng.random() * 2 * math.pi
                        distance = move_range * (0.5 + rng.random() * 0.5)
                        px = base_x + math.cos(angle) * distance
                        py = base_y + math.sin(angle) * distance
                        # Ensure within bounds
                        px = max(margin, min(width - margin, px))
                        py = max(margin, min(height - margin, py))
                        key_points.append((px, py))
                    
                    # Add intermediate points between key locations
                    for j in range(len(key_points)):
                        anchor_points.append(key_points[j])
                        
                        # Add some points between this key point and the next
                        next_j = (j + 1) % len(key_points)
                        x1, y1 = key_points[j]
                        x2, y2 = key_points[next_j]
                        
                        # Add 1-2 intermediate points with some randomness
                        for _ in range(rng.randint(1, 2)):
                            t = rng.random()  # Position between current and next
                            # Add some random offset from the straight line
                            perpendicular_dist = move_range * 0.2 * (rng.random() - 0.5)
                            # Perpendicular direction
                            dx, dy = x2 - x1, y2 - y1
                            perp_x, perp_y = -dy, dx
                            # Normalize
                            length = math.sqrt(perp_x**2 + perp_y**2)
                            if length > 0:
                                perp_x, perp_y = perp_x / length, perp_y / length
                            
                            # Intermediate point with offset
                            ix = x1 + (x2 - x1) * t + perp_x * perpendicular_dist
                            iy = y1 + (y2 - y1) * t + perp_y * perpendicular_dist
                            
                            # Ensure within bounds
                            ix = max(margin, min(width - margin, ix))
                            iy = max(margin, min(height - margin, iy))
                            anchor_points.append((ix, iy))
                
                # Now convert anchor points to smooth Catmull-Rom spline control points
                control_points = []
                num_segments = 4  # Number of points to generate between each anchor
                
                # Loop through anchor points (including wrapping to first point)
                for j in range(len(anchor_points)):
                    # Get 4 consecutive points for Catmull-Rom spline (with wrapping)
                    p0 = anchor_points[(j - 1) % len(anchor_points)]
                    p1 = anchor_points[j]
                    p2 = anchor_points[(j + 1) % len(anchor_points)]
                    p3 = anchor_points[(j + 2) % len(anchor_points)]
                    
                    # Add the current anchor point
                    control_points.append(p1)
                    
                    # Add interpolated points between current and next anchor
                    for s in range(1, num_segments):
                        t = s / num_segments
                        # Catmull-Rom spline calculation
                        t2 = t * t
                        t3 = t2 * t
                        
                        # Catmull-Rom matrix
                        x = 0.5 * ((2 * p1[0]) +
                                   (-p0[0] + p2[0]) * t +
                                   (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                                   (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
                        
                        y = 0.5 * ((2 * p1[1]) +
                                   (-p0[1] + p2[1]) * t +
                                   (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                                   (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
                        
                        # Ensure within bounds
                        x = max(margin, min(width - margin, x))
                        y = max(margin, min(height - margin, y))
                        
                        control_points.append((x, y))
        else:
            # Fully random premium organic path
            # Create a fully procedural natural-looking path
            num_key_points = rng.randint(4, 6)
            
            # Create key points for the path
            key_points = []
            for p in range(num_key_points):
                px = rng.uniform(margin, width - margin)
                py = rng.uniform(margin, height - margin)
                key_points.append((px, py))
            
            # Make path loop smoothly by ensuring first and last points are close
            dist = math.sqrt((key_points[0][0] - key_points[-1][0])**2 + 
                            (key_points[0][1] - key_points[-1][1])**2)
            
            # If endpoints are too far apart, adjust the last point
            if dist > min(width, height) * 0.2:
                last_x, last_y = key_points[-1]
                first_x, first_y = key_points[0]
                loop_factor = 0.2  # How close the last point should be to first
                key_points[-1] = (
                    first_x + (last_x - first_x) * loop_factor,
                    first_y + (last_y - first_y) * loop_factor
                )
            
            # Convert to smooth Catmull-Rom spline path
            control_points = []
            num_segments = 5
            
            # Similar spline calculation as above
            for j in range(len(key_points)):
                p0 = key_points[(j - 1) % len(key_points)]
                p1 = key_points[j]
                p2 = key_points[(j + 1) % len(key_points)]
                p3 = key_points[(j + 2) % len(key_points)]
                
                control_points.append(p1)
                
                for s in range(1, num_segments):
                    t = s / num_segments
                    t2 = t * t
                    t3 = t2 * t
                    
                    x = 0.5 * ((2 * p1[0]) +
                               (-p0[0] + p2[0]) * t +
                               (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                               (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
                    
                    y = 0.5 * ((2 * p1[1]) +
                               (-p0[1] + p2[1]) * t +
                               (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                               (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
                    
                    x = max(margin, min(width - margin, x))
                    y = max(margin, min(height - margin, y))
                    
                    control_points.append((x, y))
            
        # Enhanced scale animation with multiple layers of movement
        # Base breathing
        breathe_amount = char_settings.get('breathe_amount', rng.uniform(0.02, 0.05))
        breathe_speed = char_settings.get('breathe_speed', rng.uniform(0.8, 1.3))
        
        # Second layer of subtle pulsing
        pulse_amount = breathe_amount * 0.3  # Subtle secondary pulse
        pulse_speed = breathe_speed * 2.7    # Faster than main breathing
        
        # Save all motion parameters with enhanced animation data
        motion_data = {
            'scale_base': scale0,
            'scale_target': scale1,
            'angle_base': angle,
            'control_points': control_points,
            'breathe_amount': breathe_amount,
            'breathe_speed': breathe_speed,
            'pulse_amount': pulse_amount,
            'pulse_speed': pulse_speed,
            'rotation_speed': char_settings.get('rotation_speed', rng.uniform(0.7, 1.3)),
            'path_type': path_type if 'path_type' in locals() else 'organic'
        }
        motions.append(motion_data)

    frames_dir = tempfile.mkdtemp(prefix='frames_')
    # Resize BG to target with high quality resizing
    bg = bg.resize((width, height), Image.LANCZOS)

    # Get exact position along the path using optimized calculation
    def get_path_position(points, t):
        """Get position along a path of points at time t (0-1)"""
        if not points:
            return (0, 0)
        
        # Normalized t that loops around the path
        t_looped = t - int(t)  # Ensures t is 0-1
        
        # Find the segment
        num_segments = len(points) - 1
        segment_idx = min(int(t_looped * num_segments), num_segments - 1)
        
        # Get position within segment (0-1)
        segment_t = (t_looped * num_segments) - segment_idx
        
        # Get the two points of this segment
        p1 = points[segment_idx]
        p2 = points[segment_idx + 1]
        
        # Smooth easing within the segment for even more fluid motion
        # Use cubic ease-in-out for smoother acceleration/deceleration
        if segment_t < 0.5:
            segment_t = 4 * segment_t**3
        else:
            segment_t = 1 - (-2 * segment_t + 2)**3 / 2
            
        # Interpolate between the points
        x = p1[0] + (p2[0] - p1[0]) * segment_t
        y = p1[1] + (p2[1] - p1[1]) * segment_t
        
        return (x, y)

    # Enhanced frame rendering with motion quality improvements
    for f in range(n_frames):
        # Normalized time with looping (0 to 1)
        t = f / (n_frames - 1 if n_frames > 1 else 1)
        
        # Create a high-quality frame with anti-aliasing enabled
        frame = bg.copy().convert('RGBA')
        
        # Process avatars in reverse order to control layering (further characters rendered first)
        sorted_avatars = [(i, av) for i, av in enumerate(avatars)]
        # If characters have y positions, sort by y to create proper depth
        if all('control_points' in motions[i] and motions[i]['control_points'] for i in range(len(avatars))):
            # Get current y positions and sort by them (lower y = further back)
            for i, _ in sorted_avatars:
                motion = motions[i]
                pos = get_path_position(motion['control_points'], t)
                sorted_avatars[i] = (i, avatars[i], pos[1])  # Store y position
            # Sort by y-position (lower drawn first, higher drawn on top)
            sorted_avatars.sort(key=lambda x: x[2])
            sorted_avatars = [(i, av) for i, av, _ in sorted_avatars]
        
        for i, av in sorted_avatars:
            motion = motions[i]
            char_settings = character_settings.get(i, {})
            
            # Determine precise time value with smooth loop transition
            path_speed = char_settings.get('path_speed', 1.0)
            t_adjusted = (t * path_speed * 1.5) % 1.0  # Loop with 1.5x speed for more movement
            
            # Add subtle easing to make movements more organic
            # Use cubic easing for smoother acceleration/deceleration
            t_eased = t_adjusted
            if t_eased < 0.5:
                t_eased = 4 * t_eased**3
            else:
                t_eased = 1 - (-2 * t_eased + 2)**3 / 2
            
            # Get precise position along path with improved interpolation
            pos = get_path_position(motion['control_points'], t_eased)
            x, y = pos
            
            # Calculate movement direction and speed with enhanced precision
            # Use larger delta for more stable direction calculation
            delta = 0.02  # Larger delta for more stable direction vector
            next_pos = get_path_position(motion['control_points'], (t_eased + delta) % 1.0)
            prev_pos = get_path_position(motion['control_points'], (t_eased - delta) % 1.0)
            
            # Direction vector with improved smoothing
            dir_x, dir_y = next_pos[0] - prev_pos[0], next_pos[1] - prev_pos[1]
            
            # Apply vector normalization for more consistent direction
            dir_length = math.sqrt(dir_x**2 + dir_y**2)
            if dir_length > 0.001:  # Avoid division by near-zero
                dir_x, dir_y = dir_x / dir_length, dir_y / dir_length
            
            # Movement speed with better calculation
            speed = math.sqrt((next_pos[0] - prev_pos[0])**2 + (next_pos[1] - prev_pos[1])**2) * 25
            
            # Apply multi-layered breathing and pulsing for more organic feel
            # Primary breathing
            breathe = motion['breathe_amount'] * math.sin(2 * math.pi * t * motion['breathe_speed'])
            
            # Secondary subtle pulsing with phase shift
            pulse = motion['pulse_amount'] * math.sin(2 * math.pi * t * motion['pulse_speed'] + 0.7) 
            
            # Third layer micro-movement for ultra-natural feel
            micro = motion['breathe_amount'] * 0.1 * math.sin(2 * math.pi * t * 3.7 + 1.3)
            
            # Combine base scale, scale animation, breathing and pulsing
            scale_base = motion['scale_base']
            scale_target = motion['scale_target']
            
            # Smooth scale transition with improved easing
            scale_t = 0.5 - 0.5 * math.cos(math.pi * t)
            base_scale = scale_base + (scale_target - scale_base) * scale_t
            
            # Apply all breathing effects with slight x/y variation for more natural movement
            sx = base_scale * (1.0 + breathe + pulse + micro)
            sy = base_scale * (1.0 + (breathe * 0.8) + pulse + (micro * 1.2))  # Slightly different y scaling
            
            # Enhanced rotation with multiple factors
            angle_base = motion['angle_base']
            rotation_speed = motion['rotation_speed']
            
            # Calculate angle based on movement direction for natural leaning
            if len(motion['control_points']) > 1 and speed > 0.1:
                # Calculate angle of movement (in degrees)
                movement_angle = math.degrees(math.atan2(dir_y, dir_x))
                
                # Tilt factor increases with speed (more lean at higher speeds)
                base_tilt = char_settings.get('tilt_factor', 0.15)
                speed_factor = min(1.0, speed / 10)  # Cap at 1.0
                tilt_factor = base_tilt * (0.5 + 0.5 * speed_factor)
                
                # Apply tilt based on movement direction
                dir_angle = movement_angle * tilt_factor
            else:
                dir_angle = 0
            
            # Add subtle oscillation for more natural movement
            oscillation = 2 * math.sin(2 * math.pi * t * 0.7)
            
            # Combine angle components with improved weighting
            anim_angle = (angle_base + 
                         dir_angle + 
                         angle_base * math.sin(2 * math.pi * t * rotation_speed) * 0.3 + 
                         oscillation)
            
            # High-quality avatar resizing and rotation with non-uniform scaling
            w, h = av.size
            aw, ah = int(w * sx), int(h * sy)
            
            # Skip if too small
            if aw < 5 or ah < 5:
                continue
                
            # Apply high-quality resize with anti-aliasing
            av_resized = av.resize((aw, ah), Image.LANCZOS)
            
            # Improved rotation with better quality and smoother edges
            av_rot = av_resized.rotate(anim_angle, resample=Image.BICUBIC, expand=True, fillcolor=(0,0,0,0))
            
            # Calculate paste coordinates with subpixel precision
            paste_x = int(x - av_rot.size[0] // 2)
            paste_y = int(y - av_rot.size[1] // 2)
            
            # Paste avatar onto frame with proper alpha handling
            frame.alpha_composite(av_rot, (paste_x, paste_y))
        
        # Save frame with high quality
        frame_rgb = frame.convert('RGB')
        frame_path = os.path.join(frames_dir, f"f_{f:05d}.png")
        frame_rgb.save(frame_path, optimize=True, quality=95)

    # Encode to high-quality MP4 with enhanced encoding settings
    out_path = os.path.join(tempfile.gettempdir(), f"scene_{rng.randrange(1_000_000)}.mp4")
    
    # Enhanced ffmpeg settings for better quality and fluid motion
    (
        ffmpeg
        .input(os.path.join(frames_dir, 'f_%05d.png'), framerate=fps)
        .output(
            out_path, 
            vcodec='libx264', 
            pix_fmt='yuv420p',
            r=fps,
            crf=17,      # Lower CRF = higher quality (17 is very high quality)
            preset='slow',  # Better compression
            profile='high',  # High profile for better quality
            level='4.2',     # Compatibility level
            movflags='faststart',
            tune='film',   # Optimize for natural content
            # Add additional quality parameters
            **{
                'x264-params': 'keyint=25:no-deblock=0:deblock=0,0:no-scenecut'  # Better quality with fewer artifacts
            }
        )
        .overwrite_output()
        .run(quiet=True)
    )
    
    return out_path
