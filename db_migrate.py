#!/usr/bin/env python3
"""
Database initialization and migration script
"""

import os
import sys
import sqlite3

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, SessionLocal
import app.models

def recreate_tables():
    """Drop and recreate all tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables dropped and recreated successfully!")

def migrate_database():
    """Check for missing columns and add them if needed"""
    # Get DB path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'app', 'app.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        Base.metadata.create_all(bind=engine)
        print("Database created successfully!")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(characters)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Check for missing columns
    required_columns = {
        'edited_path': 'TEXT',
        'scale': 'FLOAT',
        'rotation': 'FLOAT',
        'brightness': 'FLOAT',
        'contrast': 'FLOAT',
        'fixed_position': 'BOOLEAN',
        'move_range': 'FLOAT',
        'breathe_amount': 'FLOAT',
        'breathe_speed': 'FLOAT',
        'tilt_factor': 'FLOAT',
        'path_type': 'TEXT',
        'meta': 'JSON'
    }
    
    # Add missing columns
    for column, col_type in required_columns.items():
        if column not in columns:
            print(f"Adding missing column: {column}")
            cursor.execute(f"ALTER TABLE characters ADD COLUMN {column} {col_type}")
    
    # Commit changes
    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        recreate_tables()
    else:
        migrate_database()
