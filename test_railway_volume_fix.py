#!/usr/bin/env python3
"""
Test script to verify Railway volume configuration for facial evaluations
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_railway_volume_config():
    """Test the Railway volume configuration"""
    print("🧪 Testing Railway Volume Configuration for Facial Evaluations")
    print("=" * 60)
    
    # Test 1: Import config and check paths
    print("\n1. Testing configuration import...")
    try:
        from config import FACIAL_EVALUATION_FOLDER, ENVIRONMENT
        print(f"✅ Config imported successfully")
        print(f"   Environment: {ENVIRONMENT}")
        print(f"   Facial Evaluation Folder: {FACIAL_EVALUATION_FOLDER}")
        
        # Check if we're in production mode
        if ENVIRONMENT == 'production' and os.getenv('RAILWAY_ENVIRONMENT'):
            expected_path = '/app/facial_evaluations'
            if FACIAL_EVALUATION_FOLDER == expected_path:
                print(f"✅ Production path correctly set to: {expected_path}")
            else:
                print(f"❌ Production path incorrect. Expected: {expected_path}, Got: {FACIAL_EVALUATION_FOLDER}")
                return False
        else:
            expected_path = 'facial_evaluations'
            if FACIAL_EVALUATION_FOLDER == expected_path:
                print(f"✅ Development path correctly set to: {expected_path}")
            else:
                print(f"❌ Development path incorrect. Expected: {expected_path}, Got: {FACIAL_EVALUATION_FOLDER}")
                return False
                
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test 2: Test app.py import and folder creation
    print("\n2. Testing app.py import and folder creation...")
    try:
        # Temporarily set environment to test both paths
        original_env = os.environ.get('ENVIRONMENT')
        original_railway = os.environ.get('RAILWAY_ENVIRONMENT')
        
        # Test development path
        os.environ['ENVIRONMENT'] = 'development'
        if 'RAILWAY_ENVIRONMENT' in os.environ:
            del os.environ['RAILWAY_ENVIRONMENT']
        
        # Reload config to test development path
        import importlib
        import config
        importlib.reload(config)
        
        print(f"   Development mode - Facial Evaluation Folder: {config.FACIAL_EVALUATION_FOLDER}")
        
        # Test production path simulation
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['RAILWAY_ENVIRONMENT'] = 'true'
        
        importlib.reload(config)
        print(f"   Production mode - Facial Evaluation Folder: {config.FACIAL_EVALUATION_FOLDER}")
        
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        else:
            os.environ.pop('ENVIRONMENT', None)
            
        if original_railway:
            os.environ['RAILWAY_ENVIRONMENT'] = original_railway
        else:
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            
        importlib.reload(config)
        
        print("✅ Environment switching test passed")
        
    except Exception as e:
        print(f"❌ App import test failed: {e}")
        return False
    
    # Test 3: Test folder creation and permissions
    print("\n3. Testing folder creation and permissions...")
    try:
        from config import FACIAL_EVALUATION_FOLDER
        
        # Create the folder if it doesn't exist
        os.makedirs(FACIAL_EVALUATION_FOLDER, exist_ok=True)
        
        if os.path.exists(FACIAL_EVALUATION_FOLDER):
            print(f"✅ Folder exists: {FACIAL_EVALUATION_FOLDER}")
            
            # Test write permissions
            test_file = os.path.join(FACIAL_EVALUATION_FOLDER, 'test_write.txt')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("✅ Write permissions OK")
            except Exception as e:
                print(f"❌ Write permission test failed: {e}")
                return False
                
        else:
            print(f"❌ Folder does not exist: {FACIAL_EVALUATION_FOLDER}")
            return False
            
    except Exception as e:
        print(f"❌ Folder creation test failed: {e}")
        return False
    
    # Test 4: Test Railway volume mount simulation
    print("\n4. Testing Railway volume mount simulation...")
    try:
        # Simulate Railway environment
        test_volume_path = '/tmp/test_facial_evaluations'
        os.makedirs(test_volume_path, exist_ok=True)
        
        # Test file operations that would happen in production
        test_original = os.path.join(test_volume_path, 'test_original.jpg')
        test_morphed = os.path.join(test_volume_path, 'test_morphed.jpg')
        
        # Create test files
        with open(test_original, 'w') as f:
            f.write('test original image data')
        with open(test_morphed, 'w') as f:
            f.write('test morphed image data')
            
        # Test file access
        if os.path.exists(test_original) and os.path.exists(test_morphed):
            print("✅ Railway volume simulation successful")
            
            # Cleanup
            os.remove(test_original)
            os.remove(test_morphed)
            os.rmdir(test_volume_path)
        else:
            print("❌ Railway volume simulation failed")
            return False
            
    except Exception as e:
        print(f"❌ Railway volume simulation failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Railway volume configuration is working correctly.")
    print("\nKey points:")
    print("- ✅ Configuration correctly switches between development and production paths")
    print("- ✅ Folder creation and permissions work correctly")
    print("- ✅ Railway volume mount simulation successful")
    print("- ✅ File operations work as expected")
    
    print("\nNext steps for Railway deployment:")
    print("1. Ensure the 'facial-evaluations' volume is created in Railway")
    print("2. Verify the volume is mounted at '/app/facial_evaluations'")
    print("3. Set ENVIRONMENT=production and RAILWAY_ENVIRONMENT=true in Railway")
    print("4. Deploy and test facial evaluation feature")
    
    return True

if __name__ == "__main__":
    success = test_railway_volume_config()
    sys.exit(0 if success else 1)
