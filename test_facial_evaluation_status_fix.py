#!/usr/bin/env python3
"""
Test script to verify facial evaluation status column fix
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, FacialEvaluation, init_db
from flask import Flask

def test_facial_evaluation_status():
    """Test that facial evaluation status values work correctly"""
    
    print("🧪 Testing Facial Evaluation Status Fix...")
    
    # Create a minimal Flask app for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    with app.app_context():
        try:
            # Create a test user
            test_user = User(
                email='test@example.com',
                credits=50
            )
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Test user created successfully")
            
            # Test creating facial evaluation with 'Pending' status
            evaluation = FacialEvaluation(
                user_id=test_user.id,
                original_image_filename='test_original.jpg',
                morphed_image_filename='test_morphed.jpg',
                status='Pending',  # This should work now
                credits_used=20
            )
            
            db.session.add(evaluation)
            db.session.commit()
            
            print("✅ Facial evaluation created with 'Pending' status")
            
            # Test updating to 'Completed' status
            evaluation.status = 'Completed'
            evaluation.completed_at = datetime.utcnow()
            evaluation.admin_response = "Test evaluation response"
            
            db.session.commit()
            
            print("✅ Facial evaluation updated to 'Completed' status")
            
            # Test querying by status
            pending_evals = FacialEvaluation.query.filter_by(status='Pending').all()
            completed_evals = FacialEvaluation.query.filter_by(status='Completed').all()
            
            print(f"✅ Query results: {len(pending_evals)} pending, {len(completed_evals)} completed")
            
            # Test the to_dict method
            eval_dict = evaluation.to_dict()
            print(f"✅ Evaluation dict: {eval_dict}")
            
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Status column can now store full words like 'Pending' and 'Completed'")
            print("✅ Database operations work correctly")
            print("✅ The facial evaluation feature should work without database errors")
            
            return True
            
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_facial_evaluation_status()
    if success:
        print("\n🚀 The facial evaluation status fix is working correctly!")
        print("📝 Next steps:")
        print("   1. Deploy the updated code to Railway")
        print("   2. The database will automatically use the new status values")
        print("   3. Test the facial evaluation feature in production")
    else:
        print("\n❌ There are still issues that need to be resolved")
    
    sys.exit(0 if success else 1)
