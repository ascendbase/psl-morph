#!/usr/bin/env python3
"""
Deployment initialization script
Ensures database tables are created and app is ready
"""

import os
import sys
from sqlalchemy import text

def init_deployment():
    """Initialize deployment with database setup"""
    
    try:
        # Import app and models
        from app import app, db
        from models import User, FacialEvaluation
        
        print("Initializing deployment...")
        
        with app.app_context():
            # Create all database tables
            db.create_all()
            print("Database tables created")
            
            # Run facial evaluation table migration
            print("Running facial evaluation table migration...")
            migrate_facial_evaluation_table(db)
            
            # Verify facial evaluation table exists and works
            try:
                FacialEvaluation.query.first()
                print("FacialEvaluation table verified")
            except Exception as e:
                print(f"FacialEvaluation table issue: {e}")
                return False
            
            print("Deployment initialization completed!")
            return True
            
    except Exception as e:
        print(f"Deployment initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_facial_evaluation_table(db):
    """Migrate facial evaluation table to add missing columns"""
    
    try:
        # Check if facial_evaluation table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'facial_evaluation' not in tables:
            print("Facial evaluation table will be created by db.create_all()")
            return True
        
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
        print(f"Existing facial_evaluation columns: {existing_columns}")
        
        # Define required columns that might be missing
        required_columns = {
            'second_image_filename': 'VARCHAR(255)',
            'morphed_image_filename': 'VARCHAR(255)', 
            'generation_id': 'VARCHAR(36)',
            'admin_response': 'TEXT',
            'admin_id': 'VARCHAR(36)',
            'credits_used': 'INTEGER DEFAULT 20'
        }
        
        # Add missing columns
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                print(f"Adding missing column: {column_name}")
                
                # Add the column
                alter_sql = f"ALTER TABLE facial_evaluation ADD COLUMN {column_name} {column_type}"
                db.session.execute(text(alter_sql))
                
                print(f"Added column: {column_name}")
            else:
                print(f"Column already exists: {column_name}")
        
        # Commit changes
        db.session.commit()
        print("Facial evaluation table migration completed!")
        
        return True
        
    except Exception as e:
        print(f"Facial evaluation migration failed: {e}")
        # Don't fail the entire deployment for migration issues
        return True

if __name__ == "__main__":
    success = init_deployment()
    if not success:
        sys.exit(1)
