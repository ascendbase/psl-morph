#!/usr/bin/env python3
"""
Fix facial evaluation database schema by adding missing columns
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_database_schema():
    """Fix the facial evaluation database schema"""
    try:
        # Import after setting up logging
        from models import db, FacialEvaluation
        from app import app
        
        logging.info("🔧 Starting database schema fix...")
        
        with app.app_context():
            # Check if the table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'facial_evaluation' not in tables:
                logging.info("📋 Creating facial_evaluation table...")
                db.create_all()
                logging.info("✅ facial_evaluation table created successfully")
            else:
                logging.info("📋 facial_evaluation table exists, checking columns...")
                
                # Get existing columns
                columns = inspector.get_columns('facial_evaluation')
                column_names = [col['name'] for col in columns]
                
                logging.info(f"📋 Existing columns: {column_names}")
                
                # Required columns
                required_columns = [
                    'id', 'user_id', 'original_image_filename', 'secondary_image_filename',
                    'morphed_image_filename', 'generation_id', 'status', 'created_at',
                    'completed_at', 'admin_response', 'admin_id', 'credits_used'
                ]
                
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    logging.info(f"❌ Missing columns: {missing_columns}")
                    logging.info("🔧 Adding missing columns...")
                    
                    # Add missing columns using raw SQL
                    with db.engine.connect() as conn:
                        for column in missing_columns:
                            if column == 'secondary_image_filename':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN secondary_image_filename VARCHAR(255)"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added secondary_image_filename column")
                            elif column == 'morphed_image_filename':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN morphed_image_filename VARCHAR(255)"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added morphed_image_filename column")
                            elif column == 'generation_id':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN generation_id VARCHAR(36)"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added generation_id column")
                            elif column == 'status':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added status column")
                            elif column == 'completed_at':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN completed_at TIMESTAMP"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added completed_at column")
                            elif column == 'admin_response':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN admin_response TEXT"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added admin_response column")
                            elif column == 'admin_id':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN admin_id VARCHAR(36)"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added admin_id column")
                            elif column == 'credits_used':
                                sql = "ALTER TABLE facial_evaluation ADD COLUMN credits_used INTEGER DEFAULT 20"
                                conn.execute(db.text(sql))
                                logging.info("✅ Added credits_used column")
                        
                        # Commit the changes
                        conn.commit()
                        logging.info("✅ All missing columns added successfully")
                else:
                    logging.info("✅ All required columns already exist")
            
            # Verify the final schema
            inspector = db.inspect(db.engine)
            final_columns = inspector.get_columns('facial_evaluation')
            final_column_names = [col['name'] for col in final_columns]
            
            logging.info(f"📋 Final columns: {final_column_names}")
            
            # Test a simple query
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(db.text("SELECT COUNT(*) FROM facial_evaluation"))
                    count = result.scalar()
                    logging.info(f"✅ Table query test successful - {count} records found")
            except Exception as e:
                logging.error(f"❌ Table query test failed: {e}")
                return False
            
            logging.info("🎉 Database schema fix completed successfully!")
            return True
            
    except Exception as e:
        logging.error(f"❌ Database schema fix failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FACIAL EVALUATION DATABASE SCHEMA FIX")
    print("=" * 60)
    
    success = fix_database_schema()
    
    if success:
        print("\n✅ DATABASE SCHEMA FIX SUCCESSFUL!")
        print("🎯 The facial evaluation feature should now work correctly")
        print("🔄 Please restart your application to see the changes")
    else:
        print("\n❌ DATABASE SCHEMA FIX FAILED!")
        print("🔧 Please check the error messages above")
        sys.exit(1)
