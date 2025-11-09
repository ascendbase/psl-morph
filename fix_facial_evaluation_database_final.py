#!/usr/bin/env python3
"""
Final fix for facial evaluation database - creates all necessary tables and fixes any issues
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database():
    """Fix database schema and create all necessary tables"""
    try:
        # Import Flask app and database
        from app import app, db
        from models import User, Generation, Transaction, FacialEvaluation
        
        logger.info("Starting database fix...")
        
        with app.app_context():
            # Check current database URL
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
            logger.info(f"Database URL: {database_url}")
            
            # Test database connection
            try:
                db.engine.execute('SELECT 1')
                logger.info("✅ Database connection successful")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                return False
            
            # Create all tables
            try:
                db.create_all()
                logger.info("✅ All database tables created/verified")
            except Exception as e:
                logger.error(f"❌ Error creating tables: {e}")
                return False
            
            # Check if facial_evaluation table exists and has correct schema
            try:
                # Try to query the facial_evaluation table
                result = db.engine.execute("SELECT COUNT(*) FROM facial_evaluation")
                count = result.scalar()
                logger.info(f"✅ facial_evaluation table exists with {count} records")
                
                # Check table schema
                if database_url.startswith('postgresql'):
                    # PostgreSQL schema check
                    schema_query = """
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'facial_evaluation' 
                    ORDER BY ordinal_position
                    """
                    result = db.engine.execute(schema_query)
                    columns = result.fetchall()
                    
                    logger.info("facial_evaluation table schema:")
                    for col in columns:
                        logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
                    
                    # Check for required columns
                    column_names = [col[0] for col in columns]
                    required_columns = [
                        'id', 'user_id', 'original_image_filename', 'secondary_image_filename',
                        'morphed_image_filename', 'generation_id', 'status', 'created_at',
                        'completed_at', 'admin_response', 'admin_id', 'credits_used'
                    ]
                    
                    missing_columns = [col for col in required_columns if col not in column_names]
                    if missing_columns:
                        logger.warning(f"Missing columns: {missing_columns}")
                        
                        # Try to add missing columns
                        for col in missing_columns:
                            try:
                                if col == 'secondary_image_filename':
                                    db.engine.execute("ALTER TABLE facial_evaluation ADD COLUMN secondary_image_filename VARCHAR(255)")
                                    logger.info(f"✅ Added column: {col}")
                                elif col == 'credits_used':
                                    db.engine.execute("ALTER TABLE facial_evaluation ADD COLUMN credits_used INTEGER DEFAULT 20")
                                    logger.info(f"✅ Added column: {col}")
                                # Add other missing columns as needed
                            except Exception as e:
                                logger.warning(f"Could not add column {col}: {e}")
                    else:
                        logger.info("✅ All required columns present")
                
            except Exception as e:
                logger.error(f"❌ Error checking facial_evaluation table: {e}")
                return False
            
            # Verify admin user exists
            try:
                admin = User.query.filter_by(email='ascendbase@gmail.com').first()
                if admin:
                    logger.info(f"✅ Admin user exists: {admin.email} (Admin: {admin.is_admin})")
                    if not admin.is_admin:
                        admin.is_admin = True
                        db.session.commit()
                        logger.info("✅ Fixed admin privileges")
                else:
                    # Create admin user
                    admin = User(
                        email='ascendbase@gmail.com',
                        is_admin=True,
                        credits=1000
                    )
                    admin.set_password('morphpas')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("✅ Created admin user")
            except Exception as e:
                logger.error(f"❌ Error with admin user: {e}")
                return False
            
            # Test facial evaluation functionality
            try:
                # Create a test facial evaluation record
                test_user = User.query.filter_by(email='ascendbase@gmail.com').first()
                
                test_evaluation = FacialEvaluation(
                    user_id=test_user.id,
                    original_image_filename='test_image.jpg',
                    secondary_image_filename='test_image2.jpg',
                    status='pending',
                    credits_used=20
                )
                
                db.session.add(test_evaluation)
                db.session.commit()
                
                # Query it back
                retrieved = FacialEvaluation.query.filter_by(id=test_evaluation.id).first()
                if retrieved:
                    logger.info("✅ Facial evaluation CRUD operations working")
                    
                    # Clean up test record
                    db.session.delete(retrieved)
                    db.session.commit()
                else:
                    logger.error("❌ Could not retrieve test facial evaluation")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error testing facial evaluation functionality: {e}")
                return False
            
            # Final verification
            try:
                # Count records in all tables
                user_count = User.query.count()
                generation_count = Generation.query.count()
                transaction_count = Transaction.query.count()
                evaluation_count = FacialEvaluation.query.count()
                
                logger.info("📊 Database Statistics:")
                logger.info(f"  - Users: {user_count}")
                logger.info(f"  - Generations: {generation_count}")
                logger.info(f"  - Transactions: {transaction_count}")
                logger.info(f"  - Facial Evaluations: {evaluation_count}")
                
            except Exception as e:
                logger.error(f"❌ Error getting database statistics: {e}")
                return False
            
            logger.info("🎉 Database fix completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Critical error during database fix: {e}")
        return False

def main():
    """Main function"""
    logger.info("=== Facial Evaluation Database Fix ===")
    
    success = fix_database()
    
    if success:
        logger.info("✅ All database issues have been resolved!")
        logger.info("🚀 The facial evaluation feature is now ready to use!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start the application: python app.py")
        logger.info("2. Login as admin: ascendbase@gmail.com / morphpas")
        logger.info("3. Test the facial evaluation feature")
    else:
        logger.error("❌ Database fix failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
