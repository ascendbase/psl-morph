#!/usr/bin/env python3
"""
Fix facial evaluation database schema
Adds the missing second_image_filename column to the facial_evaluation table
"""

import os
import sys
from sqlalchemy import create_engine, text
from config import DATABASE_URL

def fix_database():
    """Add missing column to facial_evaluation table"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if we're using SQLite or PostgreSQL
            if 'sqlite' in DATABASE_URL.lower():
                # SQLite approach - check if column exists using PRAGMA
                result = conn.execute(text("PRAGMA table_info(facial_evaluation)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'second_image_filename' in columns:
                    print("✅ Column 'second_image_filename' already exists")
                    return True
                
                # Add the missing column for SQLite
                conn.execute(text("""
                    ALTER TABLE facial_evaluation 
                    ADD COLUMN second_image_filename VARCHAR(255)
                """))
                
            else:
                # PostgreSQL approach
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'facial_evaluation' 
                    AND column_name = 'second_image_filename'
                """))
                
                if result.fetchone():
                    print("✅ Column 'second_image_filename' already exists")
                    return True
                
                # Add the missing column for PostgreSQL
                conn.execute(text("""
                    ALTER TABLE facial_evaluation 
                    ADD COLUMN second_image_filename VARCHAR(255)
                """))
            
            conn.commit()
            print("✅ Successfully added 'second_image_filename' column to facial_evaluation table")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing facial evaluation database schema...")
    
    if fix_database():
        print("✅ Database schema fixed successfully!")
    else:
        print("❌ Failed to fix database schema")
        sys.exit(1)
