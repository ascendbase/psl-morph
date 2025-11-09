#!/usr/bin/env python3
"""
Simple setup script for facial evaluation feature
Uses the existing app structure to initialize the database
"""

import os
import sys

def setup_facial_evaluation_simple():
    """Setup facial evaluation feature using existing app structure"""
    
    # Set the DATABASE_URL if not already set
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://postgres:dKEIiFYGNmoUPbHghPYdyFzKZzQQnmCO@postgres.railway.internal:5432/railway'

    try:
        # Import the existing app and models
        from app import app, db
        from models import User, FacialEvaluation
        
        print("🚀 Setting up facial evaluation feature...")
        print(f"🔗 Using database: {os.getenv('DATABASE_URL', '').split('@')[0]}@***")
        
        with app.app_context():
            print("🔧 Creating database tables...")
            
            # Create all tables (including the new facial_evaluation table)
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Test the FacialEvaluation model
            print("🧪 Testing FacialEvaluation model...")
            
            # Check if we can query the table
            evaluations = FacialEvaluation.query.all()
            print(f"✅ FacialEvaluation table working - found {len(evaluations)} records")
            
            # Test creating a sample record (we'll delete it immediately)
            test_user = User.query.first()
            if test_user:
                test_eval = FacialEvaluation(
                    user_id=test_user.id,
                    image_filename='test.jpg',
                    status='pending'
                )
                db.session.add(test_eval)
                db.session.commit()
                
                # Delete the test record
                db.session.delete(test_eval)
                db.session.commit()
                
                print("✅ FacialEvaluation model test passed!")
            else:
                print("⚠️ No users found - create a user account to fully test the feature")
            
            print("\n🎉 Facial evaluation feature setup completed successfully!")
            print("✅ Database is ready")
            print("✅ FacialEvaluation model is working")
            print("✅ All tables are created")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    success = setup_facial_evaluation_simple()
    if not success:
        sys.exit(1)
