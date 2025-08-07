#!/usr/bin/env python3
"""
Complete Database Fix Script
Reinitializes the database and creates admin user
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import *
from models import db, User, Generation, Transaction, init_db

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

def fix_database():
    """Fix and reinitialize the database"""
    print("🔧 Starting database fix...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables and recreate them
            print("📋 Dropping all existing tables...")
            db.drop_all()
            
            print("🏗️ Creating fresh database tables...")
            db.create_all()
            
            # Create admin user
            print("👤 Creating admin user...")
            admin = User(
                email='ascendbase@gmail.com',
                is_admin=True,
                credits=1000,  # Give admin plenty of credits
                is_active=True,
                is_blocked=False
            )
            admin.set_password('morphpas')
            db.session.add(admin)
            
            # Create a test user for demonstration
            print("👤 Creating test user...")
            test_user = User(
                email='test@example.com',
                is_admin=False,
                credits=12,  # 12 starter credits as per your system
                is_active=True,
                is_blocked=False
            )
            test_user.set_password('testpass')
            db.session.add(test_user)
            
            # Create another test user with different credit status
            print("👤 Creating test user 2...")
            test_user2 = User(
                email='user2@example.com',
                is_admin=False,
                credits=0,  # No credits to test free generation
                is_active=True,
                is_blocked=False
            )
            test_user2.set_password('testpass2')
            db.session.add(test_user2)
            
            # Commit all users
            db.session.commit()
            print("✅ Users created successfully!")
            
            # Create some sample generations for testing
            print("📊 Creating sample generation records...")
            
            # Sample generation for test user
            sample_gen1 = Generation(
                user_id=test_user.id,
                preset='+1_Tier',
                workflow_type='facedetailer',
                status='completed',
                input_filename='test_input.jpg',
                output_filename='test_output.png',
                used_paid_credit=True,
                created_at=datetime.utcnow() - timedelta(hours=2),
                completed_at=datetime.utcnow() - timedelta(hours=1, minutes=30)
            )
            db.session.add(sample_gen1)
            
            # Sample generation for test user 2
            sample_gen2 = Generation(
                user_id=test_user2.id,
                preset='custom_eyes_nose',
                workflow_type='facedetailer',
                status='completed',
                input_filename='test_input2.jpg',
                output_filename='test_output2.png',
                used_free_credit=True,
                created_at=datetime.utcnow() - timedelta(hours=1),
                completed_at=datetime.utcnow() - timedelta(minutes=30)
            )
            db.session.add(sample_gen2)
            
            # Sample failed generation
            sample_gen3 = Generation(
                user_id=test_user.id,
                preset='Chad',
                workflow_type='facedetailer',
                status='failed',
                input_filename='test_input3.jpg',
                used_paid_credit=True,
                error_message='GPU connection timeout',
                created_at=datetime.utcnow() - timedelta(minutes=15)
            )
            db.session.add(sample_gen3)
            
            # Sample transaction
            print("💳 Creating sample transaction...")
            sample_transaction = Transaction(
                user_id=test_user.id,
                amount_usd=5.00,
                credits_purchased=50,
                payment_provider='stripe',
                payment_id='pi_test_12345',
                payment_status='completed',
                created_at=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow() - timedelta(days=1, hours=-1)
            )
            db.session.add(sample_transaction)
            
            # Commit all sample data
            db.session.commit()
            print("✅ Sample data created successfully!")
            
            # Verify the database
            print("\n📊 Database verification:")
            user_count = User.query.count()
            generation_count = Generation.query.count()
            transaction_count = Transaction.query.count()
            
            print(f"👥 Users: {user_count}")
            print(f"🖼️ Generations: {generation_count}")
            print(f"💳 Transactions: {transaction_count}")
            
            # List all users
            print("\n👥 User accounts:")
            users = User.query.all()
            for user in users:
                role = "Admin" if user.is_admin else "User"
                status = "Active" if user.is_active else "Inactive"
                if user.is_blocked:
                    status = "Blocked"
                print(f"  📧 {user.email} - {role} - {status} - Credits: {user.credits}")
            
            print("\n🎉 Database fix completed successfully!")
            print("\n🔑 Login credentials:")
            print("  Admin: ascendbase@gmail.com / morphpas")
            print("  Test User 1: test@example.com / testpass")
            print("  Test User 2: user2@example.com / testpass2")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            import traceback
            traceback.print_exc()
            return False

def verify_database():
    """Verify database is working correctly"""
    print("\n🔍 Verifying database functionality...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test admin user login
            admin = User.query.filter_by(email='ascendbase@gmail.com').first()
            if admin and admin.check_password('morphpas'):
                print("✅ Admin login verification: PASSED")
            else:
                print("❌ Admin login verification: FAILED")
                return False
            
            # Test credit system
            test_user = User.query.filter_by(email='test@example.com').first()
            if test_user:
                can_paid = test_user.can_generate_paid()
                can_free = test_user.can_generate_free()
                stats = test_user.get_generation_stats()
                
                print(f"✅ Credit system test: Paid={can_paid}, Free={can_free}")
                print(f"✅ User stats: {stats}")
            else:
                print("❌ Test user not found")
                return False
            
            # Test database relationships
            generations = Generation.query.all()
            for gen in generations:
                if gen.user:
                    print(f"✅ Generation-User relationship: {gen.preset} -> {gen.user.email}")
                else:
                    print(f"❌ Broken relationship for generation {gen.id}")
            
            print("✅ Database verification completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🚀 Face Morphing App - Database Fix Tool")
    print("=" * 50)
    
    # Fix the database
    if fix_database():
        # Verify it's working
        if verify_database():
            print("\n🎉 Database is now fully functional!")
            print("\n📝 Next steps:")
            print("1. Start your app with: python app.py")
            print("2. Go to /admin to access admin dashboard")
            print("3. Login with: ascendbase@gmail.com / morphpas")
        else:
            print("\n⚠️ Database was fixed but verification failed")
    else:
        print("\n❌ Database fix failed")
        sys.exit(1)
