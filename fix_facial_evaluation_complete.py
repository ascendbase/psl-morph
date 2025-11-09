#!/usr/bin/env python3
"""
Complete fix for facial evaluation database
Creates all tables and ensures the facial_evaluation table has the correct schema
"""

import os
import sys
from flask import Flask
from models import db, init_db
from config import DATABASE_URL

def fix_facial_evaluation():
    """Initialize database and fix facial evaluation table"""
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        print("🔧 Initializing database...")
        init_db(app)
        
        with app.app_context():
            # Check if facial_evaluation table exists and has the right columns
            from sqlalchemy import create_engine, text, inspect
            
            engine = create_engine(DATABASE_URL)
            inspector = inspect(engine)
            
            # Check if facial_evaluation table exists
            if 'facial_evaluation' not in inspector.get_table_names():
                print("❌ facial_evaluation table does not exist")
                return False
            
            # Check columns
            columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
            print(f"📋 Current columns: {columns}")
            
            if 'second_image_filename' not in columns:
                print("🔧 Adding missing second_image_filename column...")
                
                with engine.connect() as conn:
                    if 'sqlite' in DATABASE_URL.lower():
                        conn.execute(text("""
                            ALTER TABLE facial_evaluation 
                            ADD COLUMN second_image_filename VARCHAR(255)
                        """))
                    else:
                        conn.execute(text("""
                            ALTER TABLE facial_evaluation 
                            ADD COLUMN second_image_filename VARCHAR(255)
                        """))
                    conn.commit()
                
                print("✅ Successfully added second_image_filename column")
            else:
                print("✅ second_image_filename column already exists")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fixing facial evaluation database...")
    
    if fix_facial_evaluation():
        print("✅ Database fixed successfully!")
    else:
        print("❌ Failed to fix database")
        sys.exit(1)
