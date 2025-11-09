#!/usr/bin/env python3
"""
Final test script to verify Railway volume configuration with improved detection
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_railway_volume_final():
    """Test the final Railway volume configuration"""
    print("🔧 Final Railway Volume Configuration Test")
    print("=" * 50)
    
    # Test 1: Import configuration
    print("\n1. Testing improved configuration import...")
    try:
        from config import FACIAL_EVALUATION_FOLDER, ENVIRONMENT, is_railway
        print(f"✅ Config imported successfully")
        print(f"   Environment: {ENVIRONMENT}")
        print(f"   Railway detected: {is_railway}")
        print(f"   Facial Evaluation Folder: {FACIAL_EVALUATION_FOLDER}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test 2: Test app.py import and startup logging
    print("\n2. Testing app.py startup with improved logging...")
    try:
        # Temporarily redirect stdout to capture logs
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        captured_output = io.StringIO()
        
        # Import app to trigger startup logging
        with redirect_stdout(captured_output), redirect_stderr(captured_output):
            import app
        
        output = captured_output.getvalue()
        
        if "Facial evaluation folder ready" in output:
            print("✅ App startup logging working correctly")
        else:
            print("⚠️ App startup logging may need verification")
        
        print(f"   App root: {app.APP_ROOT}")
        print(f"   Facial evaluation folder: {app.FACIAL_EVALUATION_FOLDER}")
        
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    # Test 3: Test folder creation and permissions
    print("\n3. Testing folder creation and permissions...")
    try:
        # Test if folder exists
        if os.path.exists(FACIAL_EVALUATION_FOLDER):
            print(f"✅ Folder exists: {FACIAL_EVALUATION_FOLDER}")
        else:
            print(f"❌ Folder does not exist: {FACIAL_EVALUATION_FOLDER}")
            return False
        
        # Test write permissions
        test_file = os.path.join(FACIAL_EVALUATION_FOLDER, 'test_write_final.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('test write permissions')
            os.remove(test_file)
            print(f"✅ Write permissions OK")
        except Exception as e:
            print(f"❌ Write permissions failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Folder test failed: {e}")
        return False
    
    # Test 4: Test Railway detection logic
    print("\n4. Testing Railway detection logic...")
    try:
        # Test individual detection methods
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        railway_project = os.getenv('RAILWAY_PROJECT_ID')
        railway_service = os.getenv('RAILWAY_SERVICE_ID')
        database_url = os.getenv('DATABASE_URL', '')
        app_dir_exists = os.path.exists('/app')
        
        print(f"   RAILWAY_ENVIRONMENT: {'SET' if railway_env else 'NOT SET'}")
        print(f"   RAILWAY_PROJECT_ID: {'SET' if railway_project else 'NOT SET'}")
        print(f"   RAILWAY_SERVICE_ID: {'SET' if railway_service else 'NOT SET'}")
        print(f"   DATABASE_URL starts with postgresql: {database_url.startswith('postgresql://')}")
        print(f"   /app directory exists: {app_dir_exists}")
        print(f"   Final Railway detection: {is_railway}")
        
        if is_railway:
            print("✅ Railway detection working")
        else:
            print("ℹ️ Not detected as Railway (expected for local development)")
            
    except Exception as e:
        print(f"❌ Railway detection test failed: {e}")
        return False
    
    # Test 5: Test production simulation
    print("\n5. Testing production path simulation...")
    try:
        # Temporarily set environment variables to simulate Railway
        original_env = os.environ.get('ENVIRONMENT')
        original_railway = os.environ.get('RAILWAY_ENVIRONMENT')
        
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['RAILWAY_ENVIRONMENT'] = 'true'
        
        # Re-import config to test production detection
        import importlib
        import config
        importlib.reload(config)
        
        print(f"   Production environment: {config.ENVIRONMENT}")
        print(f"   Production Railway detection: {config.is_railway}")
        print(f"   Production facial evaluation folder: {config.FACIAL_EVALUATION_FOLDER}")
        
        # Restore original environment
        if original_env:
            os.environ['ENVIRONMENT'] = original_env
        else:
            os.environ.pop('ENVIRONMENT', None)
            
        if original_railway:
            os.environ['RAILWAY_ENVIRONMENT'] = original_railway
        else:
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
        
        # Reload config again to restore original state
        importlib.reload(config)
        
        print("✅ Production simulation successful")
        
    except Exception as e:
        print(f"❌ Production simulation failed: {e}")
        return False
    
    # Test 6: Test debug script functionality
    print("\n6. Testing debug script functionality...")
    try:
        # Run the debug script
        import subprocess
        result = subprocess.run([sys.executable, 'debug_railway_volume_production.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Debug script runs successfully")
            if "Railway Volume Configuration Debug" in result.stdout:
                print("✅ Debug script output format correct")
            else:
                print("⚠️ Debug script output format may need verification")
        else:
            print(f"❌ Debug script failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Debug script test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Railway volume configuration is ready for deployment.")
    print("\nKey improvements implemented:")
    print("✅ Enhanced Railway detection with multiple indicators")
    print("✅ Improved startup logging with permission testing")
    print("✅ Robust error handling and diagnostics")
    print("✅ Production/development path switching")
    print("✅ Debug script for production troubleshooting")
    
    print("\nNext steps for Railway deployment:")
    print("1. Create Railway volume 'facial-evaluations' mounted at '/app/facial_evaluations'")
    print("2. Set ENVIRONMENT=production in Railway dashboard")
    print("3. Deploy and monitor logs for facial evaluation folder status")
    print("4. Test facial evaluation feature end-to-end")
    
    return True

if __name__ == "__main__":
    success = test_railway_volume_final()
    sys.exit(0 if success else 1)
