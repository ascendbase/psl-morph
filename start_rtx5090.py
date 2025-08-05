#!/usr/bin/env python3
"""
Start Face Morphing App with RTX 5090 configuration
This ensures the correct environment variables are loaded
"""

import os
import sys

def load_env_file():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"Set {key.strip()} = {value.strip()}")
    else:
        print(f"Warning: {env_file} not found")

def verify_rtx5090_config():
    """Verify RTX 5090 configuration"""
    print("\n=== RTX 5090 Configuration ===")
    print(f"COMFYUI_URL: {os.getenv('COMFYUI_URL', 'NOT SET')}")
    print(f"USE_CLOUD_GPU: {os.getenv('USE_CLOUD_GPU', 'NOT SET')}")
    print(f"USE_RUNPOD_POD: {os.getenv('USE_RUNPOD_POD', 'NOT SET')}")
    
    # Verify the URL is correct
    expected_url = "https://choa76vtevld8t-8188.proxy.runpod.net"
    actual_url = os.getenv('COMFYUI_URL')
    
    if actual_url == expected_url:
        print("✅ RTX 5090 URL is correctly configured")
    else:
        print(f"❌ RTX 5090 URL mismatch!")
        print(f"   Expected: {expected_url}")
        print(f"   Actual: {actual_url}")
        return False
    
    # Verify cloud GPU is disabled (so it uses ComfyUI client)
    use_cloud_gpu = os.getenv('USE_CLOUD_GPU', 'false').lower()
    if use_cloud_gpu == 'false':
        print("✅ Using ComfyUI client (correct for RTX 5090 proxy)")
    else:
        print(f"❌ USE_CLOUD_GPU should be 'false', got '{use_cloud_gpu}'")
        return False
    
    print("✅ RTX 5090 configuration verified!")
    return True

def main():
    print("🚀 Starting Face Morphing App with RTX 5090")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Verify configuration
    if not verify_rtx5090_config():
        print("❌ Configuration error! Please check your .env file")
        sys.exit(1)
    
    print("\n🎯 Starting Flask app...")
    print("RTX 5090 is ready for face morphing!")
    print("=" * 50)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()