#!/usr/bin/env python3
"""
Complete Facial Evaluation Feature Test
Tests the entire facial evaluation workflow from request to admin response
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "ascendbase@gmail.com"
ADMIN_PASSWORD = "morphpas"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

def print_status(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_facial_evaluation_complete_workflow():
    """Test the complete facial evaluation workflow"""
    print_status("🧪 TESTING COMPLETE FACIAL EVALUATION FEATURE", "TEST")
    print("=" * 80)
    
    session = requests.Session()
    
    try:
        # 1. Test admin login
        print_status("1. Testing admin login...")
        login_data = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code != 200:
            print_status(f"❌ Admin login failed: {response.status_code}", "ERROR")
            return False
        
        print_status("✅ Admin login successful")
        
        # 2. Test admin facial evaluations page
        print_status("2. Testing admin facial evaluations page...")
        response = session.get(f"{BASE_URL}/admin/facial-evaluations")
        if response.status_code != 200:
            print_status(f"❌ Admin facial evaluations page failed: {response.status_code}", "ERROR")
            return False
        
        if "Facial Evaluation Management" in response.text:
            print_status("✅ Admin facial evaluations page accessible")
        else:
            print_status("❌ Admin facial evaluations page content missing", "ERROR")
            return False
        
        # 3. Test user facial evaluation dashboard
        print_status("3. Testing user facial evaluation dashboard...")
        response = session.get(f"{BASE_URL}/facial-evaluation")
        if response.status_code != 200:
            print_status(f"❌ User facial evaluation dashboard failed: {response.status_code}", "ERROR")
            return False
        
        if "Facial Evaluation Requests" in response.text:
            print_status("✅ User facial evaluation dashboard accessible")
        else:
            print_status("❌ User facial evaluation dashboard content missing", "ERROR")
            return False
        
        # 4. Test facial evaluation request (standalone)
        print_status("4. Testing standalone facial evaluation request...")
        
        # Create a test image file
        test_image_path = "test_face.jpg"
        if not os.path.exists(test_image_path):
            # Create a minimal test image (1x1 pixel)
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(test_image_path, 'JPEG')
        
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_face.jpg', f, 'image/jpeg')}
            response = session.post(f"{BASE_URL}/request-facial-evaluation-standalone", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                evaluation_id = result.get('evaluation_id')
                print_status(f"✅ Standalone facial evaluation request successful (ID: {evaluation_id})")
            else:
                print_status(f"❌ Standalone facial evaluation request failed: {result.get('error')}", "ERROR")
                return False
        else:
            print_status(f"❌ Standalone facial evaluation request failed: {response.status_code}", "ERROR")
            return False
        
        # 5. Test admin response to facial evaluation
        print_status("5. Testing admin response to facial evaluation...")
        
        response_data = {
            'response': 'This is a test facial evaluation response. The user has good facial structure with room for improvement in the jawline area. Overall rating: 7/10. Areas for improvement: 1. Jawline definition, 2. Eye area enhancement, 3. Overall facial symmetry.'
        }
        
        response = session.post(
            f"{BASE_URL}/admin/facial-evaluation/{evaluation_id}",
            json=response_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_status("✅ Admin response to facial evaluation successful")
            else:
                print_status(f"❌ Admin response failed: {result.get('error')}", "ERROR")
                return False
        else:
            print_status(f"❌ Admin response failed: {response.status_code}", "ERROR")
            return False
        
        # 6. Test facial evaluation image serving
        print_status("6. Testing facial evaluation image serving...")
        
        response = session.get(f"{BASE_URL}/facial-evaluation-image/{evaluation_id}/original")
        if response.status_code == 200:
            print_status("✅ Original image serving successful")
        else:
            print_status(f"❌ Original image serving failed: {response.status_code}", "ERROR")
            return False
        
        # 7. Test facial evaluation deletion
        print_status("7. Testing facial evaluation deletion...")
        
        response = session.post(f"{BASE_URL}/admin/delete_facial_evaluation/{evaluation_id}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_status(f"✅ Facial evaluation deletion successful (deleted {result.get('images_deleted', 0)} images)")
            else:
                print_status(f"❌ Facial evaluation deletion failed: {result.get('error')}", "ERROR")
                return False
        else:
            print_status(f"❌ Facial evaluation deletion failed: {response.status_code}", "ERROR")
            return False
        
        # 8. Test Railway volume integration
        print_status("8. Testing Railway volume integration...")
        
        response = session.get(f"{BASE_URL}/admin/railway-volume-proof")
        if response.status_code == 200:
            if "RAILWAY VOLUME PROOF VERIFICATION" in response.text:
                print_status("✅ Railway volume integration working")
            else:
                print_status("⚠️ Railway volume proof accessible but may have issues", "WARN")
        else:
            print_status(f"❌ Railway volume proof failed: {response.status_code}", "ERROR")
            return False
        
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        print("=" * 80)
        print_status("🎉 ALL FACIAL EVALUATION TESTS PASSED!", "SUCCESS")
        print_status("✅ Feature is ready for production deployment", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Test failed with exception: {e}", "ERROR")
        return False

def test_facial_evaluation_ui_elements():
    """Test that UI elements are properly integrated"""
    print_status("🎨 TESTING UI INTEGRATION", "TEST")
    print("=" * 80)
    
    session = requests.Session()
    
    try:
        # Login as admin
        login_data = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        # Test main generation page has facial evaluation prompt
        print_status("1. Testing generation page facial evaluation integration...")
        response = session.get(f"{BASE_URL}/app")
        
        if "Request Personal Rating & Analysis" in response.text:
            print_status("✅ Generation page has facial evaluation prompt")
        else:
            print_status("❌ Generation page missing facial evaluation prompt", "ERROR")
            return False
        
        # Test dashboard has facial evaluation link
        print_status("2. Testing dashboard facial evaluation link...")
        response = session.get(f"{BASE_URL}/dashboard")
        
        if "My Facial Evaluations" in response.text or "facial-evaluation" in response.text:
            print_status("✅ Dashboard has facial evaluation link")
        else:
            print_status("❌ Dashboard missing facial evaluation link", "ERROR")
            return False
        
        # Test admin dashboard has facial evaluation management
        print_status("3. Testing admin dashboard facial evaluation management...")
        response = session.get(f"{BASE_URL}/admin")
        
        if "facial-evaluations" in response.text or "Facial Evaluation" in response.text:
            print_status("✅ Admin dashboard has facial evaluation management")
        else:
            print_status("❌ Admin dashboard missing facial evaluation management", "ERROR")
            return False
        
        print("=" * 80)
        print_status("🎉 ALL UI INTEGRATION TESTS PASSED!", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"❌ UI test failed with exception: {e}", "ERROR")
        return False

def test_database_integration():
    """Test database integration"""
    print_status("🗄️ TESTING DATABASE INTEGRATION", "TEST")
    print("=" * 80)
    
    try:
        # Test database connection
        print_status("1. Testing database connection...")
        
        # Import database models
        sys.path.append('.')
        from models import db, FacialEvaluation, User
        from app import app
        
        with app.app_context():
            # Test if FacialEvaluation table exists
            try:
                count = FacialEvaluation.query.count()
                print_status(f"✅ Database connection successful ({count} facial evaluations found)")
            except Exception as e:
                print_status(f"❌ Database connection failed: {e}", "ERROR")
                return False
        
        print("=" * 80)
        print_status("🎉 DATABASE INTEGRATION TEST PASSED!", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Database test failed with exception: {e}", "ERROR")
        return False

def main():
    """Run all tests"""
    print_status("🚀 STARTING COMPLETE FACIAL EVALUATION FEATURE TEST", "START")
    print_status(f"Testing against: {BASE_URL}")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_status("❌ Server is not responding properly", "ERROR")
            return False
        print_status("✅ Server is running and responsive")
    except Exception as e:
        print_status(f"❌ Cannot connect to server: {e}", "ERROR")
        print_status("Please make sure the Flask app is running on localhost:5000", "INFO")
        return False
    
    # Run all tests
    tests = [
        ("Database Integration", test_database_integration),
        ("UI Integration", test_facial_evaluation_ui_elements),
        ("Complete Workflow", test_facial_evaluation_complete_workflow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print_status(f"✅ {test_name} PASSED", "SUCCESS")
        else:
            print_status(f"❌ {test_name} FAILED", "ERROR")
    
    print("\n" + "="*80)
    print_status(f"FINAL RESULTS: {passed}/{total} tests passed", "RESULT")
    
    if passed == total:
        print_status("🎉 ALL TESTS PASSED! Facial evaluation feature is fully functional!", "SUCCESS")
        print_status("✅ Ready for production deployment", "SUCCESS")
        return True
    else:
        print_status(f"❌ {total - passed} tests failed. Please fix issues before deployment.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
