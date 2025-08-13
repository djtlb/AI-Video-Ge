#!/usr/bin/env python3
"""
Database initialization script for AI Avatar Video application
"""

import os
import sys

# Make sure we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from app.database import Base, engine
# Need to import models so they are registered with SQLAlchemy
import app.models

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
