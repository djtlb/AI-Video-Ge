import os
import logging
import ffmpeg
from fastapi import Body
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image

from .database import Base, engine, SessionLocal
from .models import Character
from .schemas import CharacterOut, GenerateRequest, CharacterEditRequest
from .utils import ensure_dirs, save_thumbnail, clamp_avatar_size
from .ai import BackgroundGenerator, cutout_person, composite_video
from .advanced_motion import AdvancedMotion
from .gpu_utils import get_system_info, get_gpu_status

# Import configuration if available
try:
    from .config import ALLOWED_ORIGINS, USE_GPU, PREFER_AMD_GPU
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Import the integrations API if available
try:
    from .integrations_api import IntegrationsAPI
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ensure_dirs(BASE_DIR)

# Initialize the AdvancedMotion module
advanced_motion = AdvancedMotion()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai-avatar-video")

# DB init
Base.metadata.create_all(bind=engine)

# Initialize FastAPI with production settings
app = FastAPI(
    title='AI Avatar Video Generator', 
    version='1.0.0',
    description='Production-ready API for generating AI avatar videos',
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add static files mounting
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')

# Add custom exception handlers
try:
    from .exceptions import add_exception_handlers
    add_exception_handlers(app)
    logger.info("Custom exception handlers added")
except ImportError:
    logger.warning("Custom exception handlers not available")

# Add custom middleware
try:
    from .middleware import add_middleware
    add_middleware(app)
    logger.info("Custom middleware added")
except ImportError:
    logger.warning("Custom middleware not available")

# Get allowed origins from environment variable or use defaults
if CONFIG_AVAILABLE:
    cors_origins = ALLOWED_ORIGINS
else:
    # Get the port from environment variable, default to 8080
    port = os.environ.get("PORT", "8080")
    cors_origins = os.environ.get(
        "ALLOWED_ORIGINS", 
        f"http://localhost:3000,http://localhost:{port},http://127.0.0.1:3000,http://127.0.0.1:{port}"
    ).split(",")

# Configure CORS with specific origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "http://10.0.2.2:8081",  # Android emulator special IP for host's localhost
        "http://10.0.2.2:8082",  # Alternative port for Metro bundler
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Lazy-load model once
_bg_gen = None

def get_bg_gen():
    global _bg_gen
    if _bg_gen is None:
        import torch
        
        # Default to CPU
        device = 'cpu'
        
        # Check configuration or environment variable
        use_gpu = True
        if CONFIG_AVAILABLE:
            use_gpu = USE_GPU
        else:
            use_gpu = os.environ.get('USE_GPU', '1') == '1'
            
        # Check for AMD GPU preference
        prefer_amd = True
        if CONFIG_AVAILABLE:
            prefer_amd = PREFER_AMD_GPU
        else:
            prefer_amd = os.environ.get('PREFER_AMD_GPU', '1') == '1'
            
        if use_gpu:
            # Check for AMD GPU first if preferred
            if prefer_amd and torch.version.hip and torch.version.hip != '':
                device = 'cuda'  # ROCm/AMD, PyTorch uses 'cuda' for ROCm
                logger.info("Using AMD GPU with ROCm")
            # Then check for NVIDIA GPU
            elif torch.cuda.is_available():
                device = 'cuda'
                logger.info("Using NVIDIA GPU with CUDA")
            # Then check for Apple Silicon
            elif hasattr(torch, 'has_mps') and torch.has_mps:
                device = 'mps'  # Apple Silicon
                logger.info("Using Apple Silicon GPU with MPS")
        
        logger.info(f"Initializing BackgroundGenerator with device: {device}")
        _bg_gen = BackgroundGenerator(device=device)
    return _bg_gen


def torch_available():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize integrations API if available
integrations_api = None
if INTEGRATIONS_AVAILABLE:
    try:
        integrations_api = IntegrationsAPI()
        print("Integrations API initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Integrations API: {e}")

@app.get('/', response_class=HTMLResponse)
async def root_page():
    index_path = os.path.join(BASE_DIR, 'static', 'index.html')
    logging.info(f"Serving index.html from: {index_path}")
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content)
    except Exception as e:
        logging.error(f"Error serving index.html: {e}")
        return HTMLResponse(f"<h1>Error loading UI</h1><pre>{e}</pre>", status_code=500)


@app.post('/characters', response_model=CharacterOut)
async def create_character(name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail='Empty file')
            
        # Validate image content
        from io import BytesIO
        try:
            from PIL import Image
            test_img = Image.open(BytesIO(content))
            test_img.verify()  # Verify it's a valid image
        except Exception as img_error:
            logger.error(f"Invalid image file: {img_error}")
            raise HTTPException(status_code=400, detail='Invalid image file')

        # Save original
        char_dir = os.path.join(BASE_DIR, 'storage', 'characters')
        thumbs_dir = os.path.join(BASE_DIR, 'storage', 'thumbs')
        os.makedirs(char_dir, exist_ok=True)
        os.makedirs(thumbs_dir, exist_ok=True)

        # Generate a unique base filename
        import time
        import random
        base = os.path.splitext(file.filename)[0]
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        safe_base = f"{base.replace(' ', '_')}_{timestamp}_{random_suffix}"
        
        original_path = os.path.join(char_dir, f'{safe_base}_orig.png')
        with open(original_path, 'wb') as f:
            f.write(content)

        # Cutout with rembg
        logger.info(f"Processing cutout for {safe_base}")
        cutout_img = cutout_person(content)
        cutout_path = os.path.join(char_dir, f'{safe_base}_cutout.png')
        cutout_img.save(cutout_path)
        clamp_avatar_size(cutout_path)

        # Thumb
        thumb_path = os.path.join(thumbs_dir, f'{safe_base}_thumb.png')
        save_thumbnail(cutout_path, thumb_path)

        # Save DB
        with SessionLocal() as db:
            ch = Character(name=name, original_path=original_path, cutout_path=cutout_path, thumb_path=thumb_path)
            db.add(ch)
            db.commit()
            db.refresh(ch)
            return ch
    except HTTPException:
        raise  # Re-raise HTTP exceptions as they already have the proper format
    except Exception as e:
        logger.error(f"Error creating character: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing character: {str(e)}")


@app.get('/characters', response_model=List[CharacterOut])
async def list_characters():
    with SessionLocal() as db:
        rows = db.query(Character).order_by(Character.created_at.desc()).all()
        return rows


@app.delete('/characters/{char_id}')
async def delete_character(char_id: int):
    with SessionLocal() as db:
        ch = db.query(Character).get(char_id)
        if not ch:
            raise HTTPException(status_code=404, detail='Character not found')
        # Remove files
        for p in [ch.original_path, ch.cutout_path, ch.thumb_path]:
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        db.delete(ch)
        db.commit()
        return {'ok': True}


@app.post('/generate')
async def generate_video(req: GenerateRequest):
    # Log incoming generation request (truncated prompt for brevity)
    try:
        safe_prompt = (req.prompt or "")[:120]
    except Exception:
        safe_prompt = "<unprintable>"
    logger.info(
        f"[GENERATE] characters={req.character_ids} duration={req.duration_seconds}s size={req.width}x{req.height} "
        f"fps={req.fps} seed={req.seed} prompt=\"{safe_prompt}\""
    )
    if not (10 <= req.duration_seconds <= 25):
        raise HTTPException(status_code=400, detail='duration_seconds must be 10-25')

    # Load characters
    with SessionLocal() as db:
        chars = db.query(Character).filter(Character.id.in_(req.character_ids)).all()
    if not chars:
        raise HTTPException(status_code=400, detail='No valid characters found')

    # Load avatars - prefer edited version if available
    avatars = []
    char_settings = {}
    
    for i, ch in enumerate(chars):
        # Use edited path if it exists, otherwise use cutout path
        img_path = ch.edited_path if ch.edited_path and os.path.exists(ch.edited_path) else ch.cutout_path
        im = Image.open(img_path).convert('RGBA')
        
        # Normalization: clamp very large avatars (already done on save, but double safe)
        im.thumbnail((1024, 1024))
        avatars.append(im)
        
        # Add character settings for the video generation
        if req.character_settings and str(ch.id) in req.character_settings:
            # Use settings from the request
            char_settings[i] = req.character_settings[str(ch.id)]
        else:
            # Default settings from database if available
            settings = {}
            
            # Add visual appearance settings
            if ch.scale is not None and ch.scale != 1.0:
                settings['scale'] = ch.scale
            if ch.rotation is not None and ch.rotation != 0.0:
                settings['rotation'] = ch.rotation
                
            # Add motion settings
            if ch.fixed_position is not None:
                settings['fixed_position'] = ch.fixed_position
            if ch.move_range is not None:
                settings['move_range'] = ch.move_range
            if ch.breathe_amount is not None:
                settings['breathe_amount'] = ch.breathe_amount
            if ch.breathe_speed is not None:
                settings['breathe_speed'] = ch.breathe_speed
            if ch.tilt_factor is not None:
                settings['tilt_factor'] = ch.tilt_factor
            if ch.path_type is not None:
                settings['path_type'] = ch.path_type
                
            # Add position if stored in meta
            if ch.meta and 'position_x' in ch.meta and 'position_y' in ch.meta:
                settings['position_x'] = ch.meta['position_x']
                settings['position_y'] = ch.meta['position_y']
                
            if settings:
                char_settings[i] = settings

    # Generate background
    logger.info("[GENERATE] Initializing/generating background image...")
    bg = get_bg_gen().generate(req.prompt, req.width, req.height, seed=req.seed)

    # Composite
    logger.info("[GENERATE] Compositing video with avatars...")
    out_path = composite_video(
        bg=bg,
        avatars=avatars,
        duration_s=req.duration_seconds,
        fps=req.fps,
        size=(req.width, req.height),
        seed=req.seed,
        character_settings=char_settings,
        prompt=req.prompt,  # Pass the prompt for SMPL-enhanced animation
    )

    # Move to storage/renders
    renders_dir = os.path.join(BASE_DIR, 'storage', 'renders')
    os.makedirs(renders_dir, exist_ok=True)
    fname = os.path.basename(out_path)
    final_path = os.path.join(renders_dir, fname)
    os.replace(out_path, final_path)

    logger.info(f"[GENERATE] Completed -> {final_path}")
    return {'video_path': final_path}


@app.post('/characters/{char_id}/edit')
async def edit_character(char_id: int, edit_req: CharacterEditRequest):
    """Edit a character's properties and image"""
    from .utils import edit_character_image
    
    with SessionLocal() as db:
        ch = db.query(Character).get(char_id)
        if not ch:
            raise HTTPException(status_code=404, detail='Character not found')
        
        # Update metadata
        if edit_req.name:
            ch.name = edit_req.name
        
        # Update image attributes
        updates = {}
        if edit_req.scale is not None:
            ch.scale = edit_req.scale
            updates['scale'] = edit_req.scale
        if edit_req.rotate is not None:
            ch.rotation = edit_req.rotate
            updates['rotate'] = edit_req.rotate
        if edit_req.brightness is not None:
            ch.brightness = edit_req.brightness
            updates['brightness'] = edit_req.brightness
        if edit_req.contrast is not None:
            ch.contrast = edit_req.contrast
            updates['contrast'] = edit_req.contrast
            
        # Update motion parameters
        if edit_req.fixed_position is not None:
            ch.fixed_position = edit_req.fixed_position
        if edit_req.move_range is not None:
            ch.move_range = edit_req.move_range
        if edit_req.breathe_amount is not None:
            ch.breathe_amount = edit_req.breathe_amount
        if edit_req.breathe_speed is not None:
            ch.breathe_speed = edit_req.breathe_speed
        if edit_req.tilt_factor is not None:
            ch.tilt_factor = edit_req.tilt_factor
        if edit_req.path_type is not None:
            ch.path_type = edit_req.path_type
        
        # Store position if provided
        if edit_req.position_x is not None or edit_req.position_y is not None:
            if not ch.meta:
                ch.meta = {}
            if edit_req.position_x is not None:
                ch.meta['position_x'] = edit_req.position_x
            if edit_req.position_y is not None:
                ch.meta['position_y'] = edit_req.position_y
            
        # Create edited image if any image params changed
        if updates:
            base = os.path.splitext(os.path.basename(ch.cutout_path))[0]
            edited_dir = os.path.join(BASE_DIR, 'storage', 'edited')
            os.makedirs(edited_dir, exist_ok=True)
            edited_path = os.path.join(edited_dir, f'{base}_edited.png')
            
            # Apply image edits
            edit_character_image(
                ch.cutout_path, 
                edited_path,
                scale=ch.scale,
                rotate=ch.rotation,
                brightness=ch.brightness,
                contrast=ch.contrast
            )
            
            # Update character record
            ch.edited_path = edited_path
            
            # Create new thumbnail for the edited image
            thumb_path = os.path.join(BASE_DIR, 'storage', 'thumbs', f'{base}_edited_thumb.png')
            save_thumbnail(edited_path, thumb_path)
            ch.thumb_path = thumb_path
            
        db.commit()
        db.refresh(ch)
        return ch

@app.get('/download')
async def download(video_path: str):
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail='Not found')
    return FileResponse(video_path, media_type='video/mp4', filename=os.path.basename(video_path))

# Edit video by text prompt
@app.post('/edit-video')
async def edit_video(video_path: str = Body(...), prompt: str = Body(...)):
    # Example: parse prompt for simple edits
    # Supported: trim, add text overlay, change resolution
    import re
    edits = {}
    # Trim: "trim to 10s" or "trim 0-10s"
    m = re.search(r'trim\s*(to)?\s*(\d+)[sS]', prompt)
    if m:
        edits['trim'] = int(m.group(2))
    m = re.search(r'trim\s*(\d+)-(\d+)[sS]', prompt)
    if m:
        edits['trim_range'] = (int(m.group(1)), int(m.group(2)))
    # Text overlay: "add title: Hello World"
    m = re.search(r'add\s*title:\s*(.+)', prompt)
    if m:
        edits['title'] = m.group(1).strip()
    # Resolution: "resize to 720p"
    m = re.search(r'resize to (\d+)p', prompt)
    if m:
        edits['resize'] = int(m.group(1))

    # Prepare output path
    out_name = f"edit_{os.path.basename(video_path).replace('.', '_')}_{abs(hash(prompt)) % 100000}.mp4"
    out_path = os.path.join(BASE_DIR, 'storage', 'renders', out_name)

    # Build ffmpeg command
    input_path = video_path if os.path.isabs(video_path) else os.path.join(BASE_DIR, video_path.lstrip('/'))
    stream = ffmpeg.input(input_path)
    if 'trim' in edits:
        stream = stream.trim(duration=edits['trim']).setpts('PTS-STARTPTS')
    if 'trim_range' in edits:
        start, end = edits['trim_range']
        stream = stream.trim(start=start, end=end).setpts('PTS-STARTPTS')
    if 'resize' in edits:
        h = edits['resize']
        w = int(h * 16 / 9)
        stream = stream.filter('scale', w, h)
    if 'title' in edits:
        stream = stream.filter('drawtext', text=edits['title'], fontcolor='white', fontsize=48, x='(w-text_w)/2', y=50, box=1, boxcolor='black@0.5')
    stream = ffmpeg.output(stream, out_path, vcodec='libx264', acodec='copy', movflags='faststart')
    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return {'edited_video_path': f'/static/renders/{out_name}'}

# List all rendered videos with metadata
@app.get('/renders')
async def list_renders():
    renders_dir = os.path.join(BASE_DIR, 'storage', 'renders')
    videos = []
    if os.path.exists(renders_dir):
        for fname in os.listdir(renders_dir):
            if fname.endswith('.mp4') or fname.endswith('.webm'):
                fpath = os.path.join(renders_dir, fname)
                stat = os.stat(fpath)
                videos.append({
                    'video_path': f'/static/renders/{fname}',
                    'name': fname,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                })
    return videos

# System info and GPU status endpoints
@app.get('/system/info')
async def system_info():
    """Get system information including CPU, memory, OS and GPU"""
    return get_system_info()

@app.get('/gpu/status')
async def gpu_status():
    """Get detailed GPU status with focus on AMD GPU support"""
    return get_gpu_status()

# Advanced integrations endpoints - only available if integrations are properly loaded
@app.get('/integrations/status')
async def integrations_status():
    """Check if integrations are available and loaded correctly"""
    return {
        "available": INTEGRATIONS_AVAILABLE,
        "initialized": integrations_api is not None,
        "modules": {
            "facechain": integrations_api.is_facechain_available() if integrations_api else False,
            "talking_avatar": integrations_api.is_talking_avatar_available() if integrations_api else False,
            "comfyui": integrations_api.is_comfyui_available() if integrations_api else False,
            "stable_diffusion": integrations_api.is_stable_diffusion_available() if integrations_api else False,
            "avatar3d": integrations_api.is_avatar3d_available() if integrations_api else False,
            "image_generator": integrations_api.is_image_generator_available() if integrations_api else False
        }
    }

@app.post('/integrations/enhance-portrait')
async def enhance_portrait(char_id: int = Body(...), prompt: str = Body(None)):
    """Enhance a character portrait using FaceChain or other available integrations"""
    if not integrations_api:
        raise HTTPException(status_code=503, detail="Integrations not available")
    
    with SessionLocal() as db:
        ch = db.query(Character).get(char_id)
        if not ch:
            raise HTTPException(status_code=404, detail='Character not found')
        
        # Source image path - use original for best results
        img_path = ch.original_path
        
        try:
            # Process with available integrations
            result_path = await integrations_api.enhance_portrait(img_path, prompt)
            
            if not result_path or not os.path.exists(result_path):
                raise HTTPException(status_code=500, detail="Portrait enhancement failed")
            
            # Update the character record to use the enhanced image
            # First, create a proper cutout from the enhanced image
            enhanced_content = open(result_path, "rb").read()
            cutout_img = cutout_person(enhanced_content)
            
            base = os.path.splitext(os.path.basename(ch.cutout_path))[0]
            enhanced_cutout_path = os.path.join(BASE_DIR, 'storage', 'characters', f'{base}_enhanced.png')
            cutout_img.save(enhanced_cutout_path)
            clamp_avatar_size(enhanced_cutout_path)
            
            # Update thumb
            thumb_path = os.path.join(BASE_DIR, 'storage', 'thumbs', f'{base}_enhanced_thumb.png')
            save_thumbnail(enhanced_cutout_path, thumb_path)
            
            # Update character record
            ch.cutout_path = enhanced_cutout_path
            ch.thumb_path = thumb_path
            # Store the original enhancement as metadata
            if not ch.meta:
                ch.meta = {}
            ch.meta['enhanced'] = True
            ch.meta['enhanced_path'] = result_path
            if prompt:
                ch.meta['enhancement_prompt'] = prompt
            
            db.commit()
            db.refresh(ch)
            
            return {
                "success": True,
                "character": ch,
                "enhanced_path": result_path
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Portrait enhancement failed: {str(e)}")

@app.post('/integrations/generate-talking-avatar')
async def generate_talking_avatar(
    char_id: int = Body(...), 
    text: str = Body(...), 
    duration_seconds: int = Body(10),
    use_advanced_motion: bool = Body(True)
):
    """Generate a talking avatar video from a character image and text"""
    if not integrations_api:
        raise HTTPException(status_code=503, detail="Integrations not available")
    
    with SessionLocal() as db:
        ch = db.query(Character).get(char_id)
        if not ch:
            raise HTTPException(status_code=404, detail='Character not found')
        
        # Source image path - use edited if available, otherwise cutout
        img_path = ch.edited_path if ch.edited_path and os.path.exists(ch.edited_path) else ch.cutout_path
        
        try:
            # Process with Talking Avatar integration
            result_path = await integrations_api.generate_talking_avatar(
                img_path, 
                text, 
                duration_seconds=duration_seconds,
                use_advanced_motion=use_advanced_motion
            )
            
            if not result_path or not os.path.exists(result_path):
                raise HTTPException(status_code=500, detail="Talking avatar generation failed")
            
            # Move to renders directory for consistency
            renders_dir = os.path.join(BASE_DIR, 'storage', 'renders')
            os.makedirs(renders_dir, exist_ok=True)
            fname = f"talking_{os.path.basename(result_path)}"
            final_path = os.path.join(renders_dir, fname)
            os.replace(result_path, final_path)
            
            return {
                "success": True,
                "video_path": final_path,
                "download_url": f"/download?video_path={final_path}"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Talking avatar generation failed: {str(e)}")

@app.post('/integrations/generate-advanced-video')
async def generate_advanced_video(
    req: GenerateRequest,
    use_comfyui: bool = Body(False),
    use_stable_diffusion: bool = Body(False)
):
    """Generate a video with advanced features using available integrations"""
    if not integrations_api:
        raise HTTPException(status_code=503, detail="Integrations not available")
    
    # First, handle the request like a normal video generation
    if not (10 <= req.duration_seconds <= 30):
        raise HTTPException(status_code=400, detail='duration_seconds must be 10-30')

    # Load characters
    with SessionLocal() as db:
        chars = db.query(Character).filter(Character.id.in_(req.character_ids)).all()
    if not chars:
        raise HTTPException(status_code=400, detail='No valid characters found')

    # Load avatars - prefer edited version if available
    avatars = []
    char_settings = {}
    
    for i, ch in enumerate(chars):
        img_path = ch.edited_path if ch.edited_path and os.path.exists(ch.edited_path) else ch.cutout_path
        im = Image.open(img_path).convert('RGBA')
        im.thumbnail((1024, 1024))
        avatars.append(im)
        
        # Add character settings as before
        if req.character_settings and str(ch.id) in req.character_settings:
            char_settings[i] = req.character_settings[str(ch.id)]
        else:
            settings = {}
            # Add all available settings from character model
            for attr in ['scale', 'rotation', 'fixed_position', 'move_range', 
                        'breathe_amount', 'breathe_speed', 'tilt_factor', 'path_type']:
                value = getattr(ch, attr, None)
                if value is not None and value != 0.0 and value != 1.0 and value != "":
                    settings[attr] = value
                    
            # Add position if stored in meta
            if ch.meta and 'position_x' in ch.meta and 'position_y' in ch.meta:
                settings['position_x'] = ch.meta['position_x']
                settings['position_y'] = ch.meta['position_y']
                
            if settings:
                char_settings[i] = settings
    
    try:
        logger.info(
            f"[ADV_GENERATE] characters={req.character_ids} duration={req.duration_seconds}s size={req.width}x{req.height} "
            f"fps={req.fps} seed={req.seed} integrations: SD={use_stable_diffusion} ComfyUI={use_comfyui}"
        )
        # Generate background - use advanced methods if available and requested
        if use_stable_diffusion and integrations_api.is_stable_diffusion_available():
            bg = await integrations_api.generate_stable_diffusion_image(
                req.prompt, req.width, req.height, seed=req.seed
            )
        elif use_comfyui and integrations_api.is_comfyui_available():
            bg = await integrations_api.generate_comfyui_image(
                req.prompt, req.width, req.height, seed=req.seed
            )
        else:
            # Fall back to default background generator
            logger.info("[ADV_GENERATE] Using default background generator")
            bg = get_bg_gen().generate(req.prompt, req.width, req.height, seed=req.seed)

        # Use the advanced motion module if available
        logger.info("[ADV_GENERATE] Compositing advanced motion video...")
        out_path = advanced_motion.composite_video(
            bg=bg,
            avatars=avatars,
            duration_s=req.duration_seconds,
            fps=req.fps,
            size=(req.width, req.height),
            seed=req.seed,
            character_settings=char_settings,
            prompt=req.prompt
        )
        # Move to storage/renders
        renders_dir = os.path.join(BASE_DIR, 'storage', 'renders')
        os.makedirs(renders_dir, exist_ok=True)
        fname = os.path.basename(out_path)
        final_path = os.path.join(renders_dir, fname)
        os.replace(out_path, final_path)

        logger.info(f"[ADV_GENERATE] Completed -> {final_path}")
        return {
            'video_path': final_path,
            'download_url': f"/download?video_path={final_path}",
            'used_integrations': {
                'stable_diffusion': use_stable_diffusion,
                'comfyui': use_comfyui,
                'advanced_motion': True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced video generation failed: {str(e)}")

@app.post('/integrations/avatar3d')
async def generate_avatar3d(
    char_id: int = Body(...),
    prompt: str = Body(None)
):
    """Generate a 3D avatar from a character image using Avatar3D integration"""
    if not integrations_api:
        raise HTTPException(status_code=503, detail="Integrations not available")
    
    if not integrations_api.is_avatar3d_available():
        raise HTTPException(status_code=503, detail="Avatar3D integration not available")
    
    with SessionLocal() as db:
        ch = db.query(Character).get(char_id)
        if not ch:
            raise HTTPException(status_code=404, detail='Character not found')
        
        # Source image path - use original for best results
        img_path = ch.original_path
        
        try:
            # Process with Avatar3D integration
            result = await integrations_api.generate_avatar3d(img_path, prompt)
            
            if not result or 'model_path' not in result:
                raise HTTPException(status_code=500, detail="3D avatar generation failed")
            
            # Update the character record with 3D model info
            if not ch.meta:
                ch.meta = {}
            ch.meta['avatar3d'] = True
            ch.meta['avatar3d_model_path'] = result['model_path']
            if 'preview_image_path' in result:
                ch.meta['avatar3d_preview'] = result['preview_image_path']
            if prompt:
                ch.meta['avatar3d_prompt'] = prompt
            
            db.commit()
            db.refresh(ch)
            
            return {
                "success": True,
                "character": ch,
                "avatar3d_info": result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"3D avatar generation failed: {str(e)}")

@app.post('/integrations/generate-ai-image')
async def generate_ai_image(
    prompt: str = Body(...),
    size: str = Body('medium')
):
    """Generate an AI image using the image generator integration"""
    if not integrations_api:
        raise HTTPException(status_code=503, detail="Integrations not available")
    
    if not integrations_api.is_image_generator_available():
        raise HTTPException(status_code=503, detail="Image generator integration not available")
    
    try:
        # Generate image using the image generator
        image_url = integrations_api.generate_ai_image(prompt, size)
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        return image_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
