#!/usr/bin/env python3
"""
Test script for RunPod integration with Face Morphing App
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_runpod_config():
    """Test RunPod configuration"""
    print("=== RunPod Configuration Test ===")
    
    # Check environment variables
    use_cloud_gpu = os.getenv('USE_CLOUD_GPU', 'false').lower() == 'true'
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    lora_url = os.getenv('RUNPOD_LORA_URL')
    
    print(f"USE_CLOUD_GPU: {use_cloud_gpu}")
    print(f"RUNPOD_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"RUNPOD_ENDPOINT_ID: {'✓ Set' if endpoint_id else '✗ Missing'}")
    print(f"RUNPOD_LORA_URL: {'✓ Set' if lora_url else '✗ Optional (not set)'}")
    
    if not use_cloud_gpu:
        print("\n⚠️  Cloud GPU is disabled. Set USE_CLOUD_GPU=true to enable RunPod.")
        return False
    
    if not api_key:
        print("\n❌ RUNPOD_API_KEY is required but not set.")
        return False
    
    if not endpoint_id:
        print("\n❌ RUNPOD_ENDPOINT_ID is required but not set.")
        return False
    
    print("\n✅ RunPod configuration looks good!")
    return True

def test_runpod_connection():
    """Test RunPod connection"""
    print("\n=== RunPod Connection Test ===")
    
    try:
        from runpod_client import RunPodClient
        
        api_key = os.getenv('RUNPOD_API_KEY')
        endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        
        if not api_key or not endpoint_id:
            print("❌ Missing RunPod credentials. Skipping connection test.")
            return False
        
        print("Creating RunPod client...")
        client = RunPodClient(api_key=api_key, endpoint_id=endpoint_id)
        
        print("Testing connection...")
        if client.test_connection():
            print("✅ Successfully connected to RunPod endpoint!")
            return True
        else:
            print("❌ Failed to connect to RunPod endpoint.")
            return False
            
    except ImportError:
        print("❌ runpod_client module not found. Make sure runpod_client.py exists.")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_app_integration():
    """Test app integration"""
    print("\n=== App Integration Test ===")
    
    try:
        # Import app components
        from config import USE_CLOUD_GPU, RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID
        
        print(f"Config loaded - USE_CLOUD_GPU: {USE_CLOUD_GPU}")
        
        if USE_CLOUD_GPU:
            print("✅ App is configured to use RunPod for cloud GPU processing.")
            
            # Test app startup (without actually running the server)
            print("Testing app initialization...")
            from app import gpu_client
            
            if gpu_client:
                print("✅ GPU client initialized successfully!")
                return True
            else:
                print("❌ GPU client failed to initialize.")
                return False
        else:
            print("⚠️  App is configured to use local ComfyUI, not RunPod.")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import app modules: {e}")
        return False
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Face Morphing App - RunPod Integration Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_runpod_config()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please check your environment variables.")
        print("\nTo fix:")
        print("1. Copy .env.runpod.example to .env")
        print("2. Fill in your RunPod API key and endpoint ID")
        print("3. Set USE_CLOUD_GPU=true")
        sys.exit(1)
    
    # Test connection
    connection_ok = test_runpod_connection()
    
    # Test app integration
    app_ok = test_app_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"App Integration: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if config_ok and connection_ok and app_ok:
        print("\n🎉 All tests passed! Your RunPod integration is ready.")
        print("\nNext steps:")
        print("1. Start the app: python app.py")
        print("2. Visit http://localhost:5000")
        print("3. Upload an image and test face morphing")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()