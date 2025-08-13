"""
Production configuration for the AI Avatar Video application.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Production settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# Server settings
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8081))  # Default to 8081 to avoid port conflicts

# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "generate-a-secure-secret-key-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# CORS settings
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    f"http://localhost:3000,http://localhost:{PORT},http://127.0.0.1:3000,http://127.0.0.1:{PORT}"
).split(",")

# Database settings
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/app.db")

# GPU settings
USE_GPU = os.environ.get("USE_GPU", "True").lower() == "true"
PREFER_AMD_GPU = os.environ.get("PREFER_AMD_GPU", "True").lower() == "true"

# Storage settings
STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(BASE_DIR, "storage"))
STATIC_DIR = os.environ.get("STATIC_DIR", os.path.join(BASE_DIR, "static"))

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "characters"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "renders"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, "thumbs"), exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Integrations
ENABLE_INTEGRATIONS = os.environ.get("ENABLE_INTEGRATIONS", "True").lower() == "true"
