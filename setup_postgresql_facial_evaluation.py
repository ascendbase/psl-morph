#!/usr/bin/env python3
"""
Setup PostgreSQL database with facial evaluation feature
This script ensures we use PostgreSQL both locally and in production
"""

import os
import sys
from flask import Flask
from models import db, init_db, FacialEvaluation
from sqlalchemy import create_engine, text, inspect

def setup_postgresql_database():
    """Setup PostgreSQL database with facial evaluation table"""
    
    # Force PostgreSQL usage
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL to your PostgreSQL connection string")
        print("Example: postgresql://username:password@localhost:5432/database_name")
        return False
    
    # Fix postgres:// to postgresql:// for newer SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Using database: {database_url.split('@')[0]}@***")
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        print("🔧 Initializing PostgreSQL database...")
        init_db(app)
        
        with app.app_context():
            # Check if facial_evaluation table exists and has correct schema
            engine = create_engine(database_url)
            inspector = inspect(engine)
            
            # Check if facial_evaluation table exists
            if 'facial_evaluation' not in inspector.get_table_names():
                print("❌ facial_evaluation table does not exist")
                print("🔧 Creating facial_evaluation table...")
                db.create_all()
                print("✅ Created facial_evaluation table")
            else:
                print("✅ facial_evaluation table exists")
            
            # Check columns
            columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
            print(f"📋 Current columns: {columns}")
            
            # Check if second_image_filename column exists
            if 'second_image_filename' not in columns:
                print("🔧 Adding missing second_image_filename column...")
                
                with engine.connect() as conn:
                    conn.execute(text("""
                        ALTER TABLE facial_evaluation 
                        ADD COLUMN second_image_filename VARCHAR(255)
                    """))
                    conn.commit()
                
                print("✅ Successfully added second_image_filename column")
            else:
                print("✅ second_image_filename column already exists")
            
            # Verify the table structure
            print("\n📊 Final table structure:")
            columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
            for col in columns:
                print(f"  - {col}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up PostgreSQL database with facial evaluation feature...")
    
    if setup_postgresql_database():
        print("\n✅ PostgreSQL database setup completed successfully!")
        print("🎉 Facial evaluation feature is ready to use!")
    else:
        print("\n❌ Failed to setup PostgreSQL database")
        print("Please check your DATABASE_URL and PostgreSQL connection")
        sys.exit(1)
