from pydantic import BaseModel
from typing import Optional, List

class CharacterOut(BaseModel):
    id: int
    name: str
    original_path: str
    cutout_path: str
    thumb_path: str
    class Config:
        from_attributes = True

class CharacterEditRequest(BaseModel):
    """Request for editing a character's properties"""
    name: Optional[str] = None
    scale: Optional[float] = None  # Scale factor for the character
    rotate: Optional[int] = None   # Rotation in degrees
    position_x: Optional[int] = None  # X position offset
    position_y: Optional[int] = None  # Y position offset
    brightness: Optional[float] = None  # Brightness adjustment (1.0 is normal)
    contrast: Optional[float] = None   # Contrast adjustment (1.0 is normal)
    # Motion parameters
    fixed_position: Optional[bool] = None  # Whether character stays in fixed position
    move_range: Optional[float] = None  # Range of movement (0.0-1.0)
    breathe_amount: Optional[float] = None  # Amount of "breathing" effect (0.0-0.1)
    breathe_speed: Optional[float] = None  # Speed of breathing (0.5-2.0)
    tilt_factor: Optional[float] = None  # How much character tilts with movement (0.0-1.0)
    path_type: Optional[str] = None  # Type of motion path ('circle', 'figure8', 'organic')

class GenerateRequest(BaseModel):
    prompt: str
    character_ids: List[int]
    duration_seconds: int  # 10-25
    width: int = 768
    height: int = 432
    fps: int = 12
    seed: Optional[int] = None
    # New fields for character placement and styling
    character_settings: Optional[dict] = None  # Dict of char_id -> settings
