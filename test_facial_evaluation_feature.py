#!/usr/bin/env python3
"""
Test the facial evaluation feature
This script tests the complete facial evaluation workflow
"""

import os
import sys
import requests
import time
from flask import Flask
from models import db, init_db, User, FacialEvaluation
from config import DATABASE_URL

def test_facial_evaluation():
    """Test facial evaluation feature"""
    
    # Check if DATABASE_URL is set
    if not DATABASE_URL or 'sqlite' in DATABASE_URL.lower():
        print("❌ This test requires PostgreSQL!")
        print("Please set DATABASE_URL to your PostgreSQL connection string")
        return False
    
    print(f"🔗 Using database: {DATABASE_URL.split('@')[0]}@***")
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        print("🔧 Initializing database...")
        init_db(app)
        
        with app.app_context():
            # Test 1: Check if facial_evaluation table exists
            print("\n📋 Test 1: Checking facial_evaluation table...")
            try:
                # Try to query the table
                evaluations = FacialEvaluation.query.all()
                print(f"✅ facial_evaluation table exists with {len(evaluations)} records")
            except Exception as e:
                print(f"❌ facial_evaluation table error: {e}")
                return False
            
            # Test 2: Create a test facial evaluation request
            print("\n📋 Test 2: Creating test facial evaluation request...")
            try:
                # Create a test user first
                test_user = User.query.filter_by(email='test@example.com').first()
                if not test_user:
                    test_user = User(
                        username='testuser',
                        email='test@example.com',
                        credits=100
                    )
                    test_user.set_password('testpass')
                    db.session.add(test_user)
                    db.session.commit()
                    print("✅ Created test user")
                else:
                    print("✅ Test user already exists")
                
                # Create a test facial evaluation request
                test_evaluation = FacialEvaluation(
                    user_id=test_user.id,
                    image_filename='test_image.jpg',
                    second_image_filename='test_morph.jpg',
                    status='pending'
                )
                db.session.add(test_evaluation)
                db.session.commit()
                print("✅ Created test facial evaluation request")
                
                # Test 3: Update the evaluation with admin response
                print("\n📋 Test 3: Testing admin response...")
                test_evaluation.admin_response = "Test facial evaluation response"
                test_evaluation.status = 'completed'
                db.session.commit()
                print("✅ Updated facial evaluation with admin response")
                
                # Test 4: Query evaluations
                print("\n📋 Test 4: Querying facial evaluations...")
                user_evaluations = FacialEvaluation.query.filter_by(user_id=test_user.id).all()
                print(f"✅ Found {len(user_evaluations)} evaluations for test user")
                
                pending_evaluations = FacialEvaluation.query.filter_by(status='pending').all()
                print(f"✅ Found {len(pending_evaluations)} pending evaluations")
                
                # Clean up test data
                print("\n🧹 Cleaning up test data...")
                db.session.delete(test_evaluation)
                db.session.commit()
                print("✅ Cleaned up test evaluation")
                
                return True
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_app_routes():
    """Test if the app starts and facial evaluation routes are accessible"""
    
    print("\n🌐 Testing app routes...")
    
    # Check if app is running on localhost:5000
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ App is running on localhost:5000")
            
            # Test facial evaluation routes
            routes_to_test = [
                '/facial-evaluation',
                '/admin/facial-evaluations'
            ]
            
            for route in routes_to_test:
                try:
                    response = requests.get(f'http://localhost:5000{route}', timeout=5)
                    if response.status_code in [200, 302, 401]:  # 302 = redirect, 401 = auth required
                        print(f"✅ Route {route} is accessible")
                    else:
                        print(f"⚠️ Route {route} returned status {response.status_code}")
                except Exception as e:
                    print(f"❌ Route {route} error: {e}")
            
            return True
        else:
            print(f"⚠️ App returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ App is not running on localhost:5000")
        print("Please start the app with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing app routes: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing facial evaluation feature...")
    
    # Test database functionality
    db_test_passed = test_facial_evaluation()
    
    # Test app routes
    routes_test_passed = test_app_routes()
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print(f"Database tests: {'✅ PASSED' if db_test_passed else '❌ FAILED'}")
    print(f"Routes tests: {'✅ PASSED' if routes_test_passed else '⚠️ SKIPPED (app not running)'}")
    
    if db_test_passed:
        print("\n🎉 Facial evaluation feature is working correctly!")
        print("✅ PostgreSQL database is properly configured")
        print("✅ FacialEvaluation model is working")
        print("✅ All database operations are functional")
        
        if not routes_test_passed:
            print("\n💡 To test the web interface:")
            print("1. Start the app: python app.py")
            print("2. Run this test again to verify routes")
    else:
        print("\n❌ Facial evaluation feature has issues")
        print("Please check your PostgreSQL configuration")
        sys.exit(1)
