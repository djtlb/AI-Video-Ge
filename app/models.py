from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from .database import Base

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    cutout_path = Column(String, nullable=False)
    thumb_path = Column(String, nullable=False)
    edited_path = Column(String, nullable=True)  # Path to edited version if any
    
    # Visual appearance parameters
    scale = Column(Float, nullable=True, default=1.0)
    rotation = Column(Float, nullable=True, default=0.0)
    brightness = Column(Float, nullable=True, default=1.0)
    contrast = Column(Float, nullable=True, default=1.0)
    
    # Motion parameters
    fixed_position = Column(Boolean, nullable=True, default=False)
    move_range = Column(Float, nullable=True, default=0.4)
    breathe_amount = Column(Float, nullable=True, default=0.03)
    breathe_speed = Column(Float, nullable=True, default=1.0)
    tilt_factor = Column(Float, nullable=True, default=0.15)
    path_type = Column(String, nullable=True, default='organic')  # 'circle', 'figure8', 'organic'
    
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
