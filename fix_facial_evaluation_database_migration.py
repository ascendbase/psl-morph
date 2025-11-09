#!/usr/bin/env python3
"""
Database migration script to fix facial evaluation table schema
Adds missing columns to existing facial_evaluation table
"""

import os
import sys
from sqlalchemy import text

def migrate_facial_evaluation_table():
    """Migrate facial evaluation table to add missing columns"""
    
    try:
        # Import app and database
        from app import app, db
        from models import FacialEvaluation
        
        print("Starting facial evaluation database migration...")
        
        with app.app_context():
            # Check if facial_evaluation table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'facial_evaluation' not in tables:
                print("Creating facial_evaluation table from scratch...")
                db.create_all()
                print("Facial evaluation table created successfully!")
                return True
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
            print(f"Existing columns: {existing_columns}")
            
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
            
            # Add foreign key constraints if they don't exist
            try:
                # Check if foreign key constraints exist
                foreign_keys = inspector.get_foreign_keys('facial_evaluation')
                existing_fks = [fk['constrained_columns'][0] for fk in foreign_keys]
                
                if 'generation_id' not in existing_fks:
                    print("Adding foreign key constraint for generation_id...")
                    fk_sql = """
                    ALTER TABLE facial_evaluation 
                    ADD CONSTRAINT fk_facial_evaluation_generation 
                    FOREIGN KEY (generation_id) REFERENCES generation(id)
                    """
                    db.session.execute(text(fk_sql))
                    print("Added generation_id foreign key constraint")
                
                if 'admin_id' not in existing_fks:
                    print("Adding foreign key constraint for admin_id...")
                    fk_sql = """
                    ALTER TABLE facial_evaluation 
                    ADD CONSTRAINT fk_facial_evaluation_admin 
                    FOREIGN KEY (admin_id) REFERENCES "user"(id)
                    """
                    db.session.execute(text(fk_sql))
                    print("Added admin_id foreign key constraint")
                    
            except Exception as e:
                print(f"Foreign key constraints may already exist or failed to add: {e}")
            
            # Commit all changes
            db.session.commit()
            print("Database migration completed successfully!")
            
            # Verify the table structure
            updated_columns = [col['name'] for col in inspector.get_columns('facial_evaluation')]
            print(f"Updated columns: {updated_columns}")
            
            # Test that we can query the table
            test_query = FacialEvaluation.query.first()
            print("Table query test passed!")
            
            return True
            
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_facial_evaluation_table()
    if not success:
        sys.exit(1)
    print("Migration completed successfully!")
