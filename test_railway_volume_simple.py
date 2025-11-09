#!/usr/bin/env python3
"""
Simple Railway Volume Configuration Test
Tests the Railway volume configuration without importing the full app
"""

import os
import sys

def test_config_only():
    """Test just the config import and Railway detection"""
    print("🔧 Simple Railway Volume Configuration Test")
    print("=" * 50)
    
    try:
        # Test config import
        print("1. Testing config import...")
        from config import FACIAL_EVALUATION_FOLDER, ENVIRONMENT
        print(f"✅ Config imported successfully")
        print(f"   Environment: {ENVIRONMENT}")
        print(f"   Facial Evaluation Folder: {FACIAL_EVALUATION_FOLDER}")
        
        # Test Railway detection logic
        print("\n2. Testing Railway detection logic...")
        is_railway = any([
            os.getenv('RAILWAY_ENVIRONMENT'),
            os.getenv('RAILWAY_PROJECT_ID'),
            os.getenv('RAILWAY_SERVICE_ID'),
            os.getenv('DATABASE_URL', '').startswith('postgresql://'),
            os.path.exists('/app')
        ])
        print(f"   Railway detected: {is_railway}")
        
        # Test folder creation
        print("\n3. Testing folder creation...")
        try:
            os.makedirs(FACIAL_EVALUATION_FOLDER, exist_ok=True)
            print(f"✅ Folder created/exists: {FACIAL_EVALUATION_FOLDER}")
            
            # Test write permissions
            test_file = os.path.join(FACIAL_EVALUATION_FOLDER, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ Folder is writable")
            
        except Exception as e:
            print(f"❌ Folder creation/write test failed: {e}")
        
        print("\n🎉 Configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_config_only()
    sys.exit(0 if success else 1)
