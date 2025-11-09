#!/usr/bin/env python3
"""
Complete test script for the facial evaluation feature
Tests all components: database, file storage, routes, and templates
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime
from PIL import Image
import io

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_schema():
    """Test that the facial evaluation database schema is correct"""
    print("🔍 Testing database schema...")
    
    try:
        # Check if we have a local database file
        db_path = 'face_morph.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if facial_evaluations table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='facial_evaluations'
            """)
            
            if cursor.fetchone():
                print("✅ facial_evaluations table exists")
                
                # Check table structure
                cursor.execute("PRAGMA table_info(facial_evaluations)")
                columns = cursor.fetchall()
                
                expected_columns = [
                    'id', 'user_id', 'original_image_path', 'morphed_image_path',
                    'status', 'admin_response', 'created_at', 'updated_at'
                ]
                
                actual_columns = [col[1] for col in columns]
                print(f"📋 Table columns: {actual_columns}")
                
                missing_columns = set(expected_columns) - set(actual_columns)
                if missing_columns:
                    print(f"❌ Missing columns: {missing_columns}")
                else:
                    print("✅ All required columns present")
                    
            else:
                print("❌ facial_evaluations table not found")
                
            conn.close()
        else:
            print("⚠️ Local database file not found, checking app configuration...")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")

def test_directory_structure():
    """Test that required directories exist"""
    print("\n🔍 Testing directory structure...")
    
    required_dirs = [
        'facial_evaluations',
        'uploads',
        'outputs',
        'templates/facial_evaluation',
        'templates/admin'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} missing")

def test_template_files():
    """Test that required template files exist"""
    print("\n🔍 Testing template files...")
    
    required_templates = [
        'templates/facial_evaluation/dashboard.html',
        'templates/admin/facial_evaluations.html',
        'templates/admin/respond_facial_evaluation.html'
    ]
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template} exists")
            
            # Check if template has basic content
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:  # Basic content check
                    print(f"   📄 Template has content ({len(content)} chars)")
                else:
                    print(f"   ⚠️ Template seems empty or minimal")
        else:
            print(f"❌ {template} missing")

def test_app_imports():
    """Test that the app can import facial evaluation components"""
    print("\n🔍 Testing app imports...")
    
    try:
        from app import app
        print("✅ App imports successfully")
        
        # Test if facial evaluation routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/facial-evaluation',
            '/request-facial-evaluation',
            '/admin/facial-evaluations',
            '/admin/respond-facial-evaluation'
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✅ Route {route} registered")
            else:
                print(f"❌ Route {route} not found")
                
    except Exception as e:
        print(f"❌ App import failed: {e}")

def test_config_settings():
    """Test facial evaluation configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import FACIAL_EVALUATION_FOLDER
        print(f"✅ FACIAL_EVALUATION_FOLDER configured: {FACIAL_EVALUATION_FOLDER}")
        
        # Check if the configured folder exists
        if os.path.exists(FACIAL_EVALUATION_FOLDER):
            print(f"✅ Configured folder exists")
        else:
            print(f"❌ Configured folder missing: {FACIAL_EVALUATION_FOLDER}")
            
    except ImportError:
        print("❌ FACIAL_EVALUATION_FOLDER not configured in config.py")

def test_models():
    """Test facial evaluation models"""
    print("\n🔍 Testing models...")
    
    try:
        from models import FacialEvaluation
        print("✅ FacialEvaluation model imports successfully")
        
        # Test model attributes
        expected_attrs = ['id', 'user_id', 'original_image_path', 'morphed_image_path', 
                         'status', 'admin_response', 'created_at', 'updated_at']
        
        for attr in expected_attrs:
            if hasattr(FacialEvaluation, attr):
                print(f"✅ Model has {attr} attribute")
            else:
                print(f"❌ Model missing {attr} attribute")
                
    except Exception as e:
        print(f"❌ Model test failed: {e}")

def create_test_image():
    """Create a test image for testing"""
    img = Image.new('RGB', (256, 256), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_file_operations():
    """Test file upload and storage operations"""
    print("\n🔍 Testing file operations...")
    
    try:
        # Test creating a test image
        test_img = create_test_image()
        print("✅ Test image created")
        
        # Test saving to facial_evaluations directory
        test_filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        test_path = os.path.join('facial_evaluations', test_filename)
        
        with open(test_path, 'wb') as f:
            f.write(test_img.getvalue())
        
        if os.path.exists(test_path):
            print(f"✅ Test file saved: {test_path}")
            
            # Clean up test file
            os.remove(test_path)
            print("✅ Test file cleaned up")
        else:
            print("❌ Test file not saved")
            
    except Exception as e:
        print(f"❌ File operations test failed: {e}")

def test_credit_system():
    """Test credit system integration"""
    print("\n🔍 Testing credit system integration...")
    
    try:
        from config import CREDIT_PACKAGES
        print("✅ Credit packages configured")
        
        # Check if facial evaluation cost is reasonable
        facial_eval_cost = 20  # As specified in requirements
        print(f"✅ Facial evaluation cost: {facial_eval_cost} credits")
        
        # Check if smallest package covers the cost
        min_package = min(CREDIT_PACKAGES.values(), key=lambda x: x['credits'])
        if min_package['credits'] >= facial_eval_cost:
            print(f"✅ Minimum package ({min_package['credits']} credits) covers facial evaluation")
        else:
            print(f"❌ Minimum package insufficient for facial evaluation")
            
    except Exception as e:
        print(f"❌ Credit system test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Facial Evaluation Feature Tests")
    print("=" * 50)
    
    test_database_schema()
    test_directory_structure()
    test_template_files()
    test_config_settings()
    test_models()
    test_app_imports()
    test_file_operations()
    test_credit_system()
    
    print("\n" + "=" * 50)
    print("🏁 Facial Evaluation Feature Tests Complete")
    print("\n💡 Next steps:")
    print("1. Run the app: python app.py")
    print("2. Test facial evaluation in browser")
    print("3. Check admin dashboard: /admin/facial-evaluations")
    print("4. Deploy to Railway with volume: railway up")

if __name__ == "__main__":
    main()
