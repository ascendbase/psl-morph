#!/usr/bin/env python3
"""
Debug script to check Railway volume configuration in production
"""

import os
import sys

def debug_railway_volume():
    """Debug Railway volume configuration"""
    print("🔍 Railway Volume Configuration Debug")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'NOT SET')}")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
    print(f"   DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
    
    # Check if we're on Railway
    railway_vars = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID', 
        'RAILWAY_SERVICE_ID',
        'RAILWAY_DEPLOYMENT_ID'
    ]
    
    print("\n2. Railway Detection:")
    railway_detected = False
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            railway_detected = True
            print(f"   ✅ {var}: {value[:20]}...")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    print(f"\n   Railway Detected: {'YES' if railway_detected else 'NO'}")
    
    # Check current configuration
    print("\n3. Current Configuration:")
    try:
        from config import FACIAL_EVALUATION_FOLDER, ENVIRONMENT
        print(f"   Config ENVIRONMENT: {ENVIRONMENT}")
        print(f"   Facial Evaluation Folder: {FACIAL_EVALUATION_FOLDER}")
        
        # Check if folder exists
        if os.path.exists(FACIAL_EVALUATION_FOLDER):
            print(f"   ✅ Folder exists: {FACIAL_EVALUATION_FOLDER}")
            
            # Check if it's writable
            test_file = os.path.join(FACIAL_EVALUATION_FOLDER, 'test_write.txt')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"   ✅ Folder is writable")
            except Exception as e:
                print(f"   ❌ Folder not writable: {e}")
        else:
            print(f"   ❌ Folder does not exist: {FACIAL_EVALUATION_FOLDER}")
            
    except Exception as e:
        print(f"   ❌ Config import failed: {e}")
    
    # Check volume mount points
    print("\n4. Volume Mount Points:")
    try:
        with open('/proc/mounts', 'r') as f:
            mounts = f.read()
            if 'facial' in mounts.lower():
                print("   ✅ Facial evaluation volume found in mounts:")
                for line in mounts.split('\n'):
                    if 'facial' in line.lower():
                        print(f"      {line}")
            else:
                print("   ❌ No facial evaluation volume found in mounts")
    except Exception as e:
        print(f"   ❌ Could not read mounts: {e}")
    
    # Check /app directory
    print("\n5. /app Directory Structure:")
    try:
        if os.path.exists('/app'):
            print("   ✅ /app directory exists")
            app_contents = os.listdir('/app')
            if 'facial_evaluations' in app_contents:
                print("   ✅ facial_evaluations found in /app")
            else:
                print("   ❌ facial_evaluations NOT found in /app")
                print(f"   Contents: {app_contents[:10]}...")  # Show first 10 items
        else:
            print("   ❌ /app directory does not exist")
    except Exception as e:
        print(f"   ❌ Could not check /app: {e}")
    
    # Recommendations
    print("\n6. Recommendations:")
    if not railway_detected:
        print("   - Set RAILWAY_ENVIRONMENT=true in Railway dashboard")
    
    if os.getenv('ENVIRONMENT') != 'production':
        print("   - Set ENVIRONMENT=production in Railway dashboard")
    
    if not os.path.exists('/app/facial_evaluations'):
        print("   - Create Railway volume 'facial-evaluations' mounted at '/app/facial_evaluations'")
        print("   - Ensure volume is properly attached to the service")
    
    print("\n" + "=" * 50)
    print("Debug complete. Check recommendations above.")

if __name__ == "__main__":
    debug_railway_volume()
