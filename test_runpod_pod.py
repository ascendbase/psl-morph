#!/usr/bin/env python3
"""
Test script for RunPod RTX 5090 Pod connection
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pod_config():
    """Test RunPod pod configuration"""
    print("=== RunPod RTX 5090 Pod Configuration Test ===")
    
    # Check environment variables
    use_cloud_gpu = os.getenv('USE_CLOUD_GPU', 'false').lower() == 'true'
    use_runpod_pod = os.getenv('USE_RUNPOD_POD', 'false').lower() == 'true'
    pod_url = os.getenv('RUNPOD_POD_URL')
    pod_port = os.getenv('RUNPOD_POD_PORT', '8188')
    
    print(f"USE_CLOUD_GPU: {use_cloud_gpu}")
    print(f"USE_RUNPOD_POD: {use_runpod_pod}")
    print(f"RUNPOD_POD_URL: {'✓ Set' if pod_url else '✗ Missing'} ({pod_url})")
    print(f"RUNPOD_POD_PORT: {pod_port}")
    
    if not use_cloud_gpu:
        print("\n⚠️  Cloud GPU is disabled. Set USE_CLOUD_GPU=true to enable RunPod.")
        return False
    
    if not use_runpod_pod:
        print("\n⚠️  RunPod pod mode is disabled. Set USE_RUNPOD_POD=true to enable.")
        return False
    
    if not pod_url:
        print("\n❌ RUNPOD_POD_URL is required but not set.")
        print("Set it to your pod IP, e.g., RUNPOD_POD_URL=149.36.1.79")
        return False
    
    print("\n✅ RunPod pod configuration looks good!")
    return True, pod_url, pod_port

def test_comfyui_connection(pod_url, pod_port):
    """Test ComfyUI connection on the pod"""
    print(f"\n=== ComfyUI Connection Test ===")
    
    comfyui_url = f"http://{pod_url}:{pod_port}"
    print(f"Testing connection to: {comfyui_url}")
    
    try:
        # Test system stats endpoint
        print("Checking system stats...")
        response = requests.get(f"{comfyui_url}/system_stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ ComfyUI is running!")
            print(f"   System: {stats.get('system', {})}")
            
            # Test queue endpoint
            print("Checking queue...")
            queue_response = requests.get(f"{comfyui_url}/queue", timeout=5)
            if queue_response.status_code == 200:
                print("✅ Queue endpoint accessible")
            
            # Test history endpoint
            print("Checking history...")
            history_response = requests.get(f"{comfyui_url}/history", timeout=5)
            if history_response.status_code == 200:
                print("✅ History endpoint accessible")
            
            return True
            
        else:
            print(f"❌ ComfyUI responded with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ComfyUI on the pod.")
        print("\nTroubleshooting steps:")
        print("1. Make sure your RunPod is running")
        print("2. Connect to your pod terminal and start ComfyUI:")
        print("   cd /workspace/ComfyUI")
        print("   python main.py --listen 0.0.0.0 --port 8188")
        print("3. Check if ComfyUI is installed on your pod")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Connection timed out. Pod might be slow to respond.")
        return False
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_pod_client():
    """Test RunPod pod client"""
    print("\n=== RunPod Pod Client Test ===")
    
    try:
        from runpod_pod_client import RunPodPodClient
        
        pod_url = os.getenv('RUNPOD_POD_URL')
        pod_port = int(os.getenv('RUNPOD_POD_PORT', '8188'))
        
        print("Creating RunPod Pod client...")
        client = RunPodPodClient(pod_url=pod_url, pod_port=pod_port)
        
        print("Testing connection...")
        if client.test_connection():
            print("✅ RunPod Pod client connected successfully!")
            return True
        else:
            print("❌ RunPod Pod client connection failed.")
            return False
            
    except ImportError:
        print("❌ runpod_pod_client module not found. Make sure runpod_pod_client.py exists.")
        return False
    except Exception as e:
        print(f"❌ Pod client test failed: {e}")
        return False

def test_app_integration():
    """Test app integration"""
    print("\n=== App Integration Test ===")
    
    try:
        # Import app components
        from config import USE_CLOUD_GPU, USE_RUNPOD_POD, RUNPOD_POD_URL, RUNPOD_POD_PORT
        
        print(f"Config loaded:")
        print(f"  USE_CLOUD_GPU: {USE_CLOUD_GPU}")
        print(f"  USE_RUNPOD_POD: {USE_RUNPOD_POD}")
        print(f"  RUNPOD_POD_URL: {RUNPOD_POD_URL}")
        print(f"  RUNPOD_POD_PORT: {RUNPOD_POD_PORT}")
        
        if USE_CLOUD_GPU and USE_RUNPOD_POD:
            print("✅ App is configured to use RunPod pod for GPU processing.")
            
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
            print("⚠️  App is not configured for RunPod pod mode.")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import app modules: {e}")
        return False
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS FOR YOUR RTX 5090 POD")
    print("=" * 60)
    
    print("\n1. Connect to your RunPod:")
    print("   - Use Web Terminal (easiest)")
    print("   - Or SSH: ssh root@149.36.1.79 -p 33805")
    
    print("\n2. Install ComfyUI on your pod:")
    print("   cd /workspace")
    print("   git clone https://github.com/comfyanonymous/ComfyUI.git")
    print("   cd ComfyUI")
    print("   pip install -r requirements.txt")
    
    print("\n3. Start ComfyUI with API:")
    print("   python main.py --listen 0.0.0.0 --port 8188")
    
    print("\n4. Configure your local app:")
    print("   cp .env.runpod.example .env")
    print("   # Edit .env with:")
    print("   USE_CLOUD_GPU=true")
    print("   USE_RUNPOD_POD=true")
    print("   RUNPOD_POD_URL=149.36.1.79")
    print("   RUNPOD_POD_PORT=8188")
    
    print("\n5. Upload your models to the pod:")
    print("   - Use Jupyter Lab file browser")
    print("   - Upload to ComfyUI/models/checkpoints/ and ComfyUI/models/loras/")
    
    print(f"\n📖 Detailed guide: See RUNPOD_RTX5090_SETUP.md")

def main():
    """Run all tests"""
    print("Face Morphing App - RunPod RTX 5090 Pod Test")
    print("=" * 50)
    
    # Test configuration
    config_result = test_pod_config()
    if not config_result:
        show_setup_instructions()
        sys.exit(1)
    
    config_ok, pod_url, pod_port = config_result
    
    # Test ComfyUI connection
    comfyui_ok = test_comfyui_connection(pod_url, pod_port)
    
    # Test pod client
    client_ok = test_pod_client() if comfyui_ok else False
    
    # Test app integration
    app_ok = test_app_integration() if client_ok else False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"ComfyUI Connection: {'✅ PASS' if comfyui_ok else '❌ FAIL'}")
    print(f"Pod Client: {'✅ PASS' if client_ok else '❌ FAIL'}")
    print(f"App Integration: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if config_ok and comfyui_ok and client_ok and app_ok:
        print("\n🎉 All tests passed! Your RTX 5090 pod is ready for face morphing.")
        print("\nNext steps:")
        print("1. Make sure your models are uploaded to the pod")
        print("2. Start the app: python app.py")
        print("3. Visit http://localhost:5000")
        print("4. Upload an image and test face morphing")
        print(f"\n💰 Remember: Your RTX 5090 pod costs ~$0.50-1.00/hour while running!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        if not comfyui_ok:
            show_setup_instructions()
        sys.exit(1)

if __name__ == "__main__":
    main()