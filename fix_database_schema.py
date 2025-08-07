"""
Fix database schema to add missing is_blocked column
"""

import sqlite3
import os

def fix_database():
    """Add missing is_blocked column to user table"""
    db_path = 'face_morph.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet - will be created properly on next run")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_blocked column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_blocked' not in columns:
            print("Adding missing is_blocked column...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_blocked BOOLEAN DEFAULT 0")
            conn.commit()
            print("✅ is_blocked column added successfully")
        else:
            print("✅ is_blocked column already exists")
        
        conn.close()
        print("✅ Database schema fixed")
        
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_database()
