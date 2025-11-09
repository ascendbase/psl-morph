#!/usr/bin/env python3
"""
Test script to verify tunnel registration with Railway app
"""

import requests
import json
import sys

def test_tunnel_registration():
    """Test registering a tunnel URL with the Railway app"""
    
    # Your Railway app URL - replace with your actual Railway URL
    railway_url = input("Enter your Railway app URL (e.g., https://your-app.railway.app): ").strip()
    if not railway_url:
        print("❌ Railway URL is required")
        return False
    
    # Test tunnel URL - replace with your actual tunnel URL
    tunnel_url = input("Enter your tunnel URL (e.g., https://keeping-za-volume-enclosed.trycloudflare.com): ").strip()
    if not tunnel_url:
        print("❌ Tunnel URL is required")
        return False
    
    # Test if tunnel is working first
    print(f"🔍 Testing tunnel connectivity: {tunnel_url}")
    try:
        response = requests.get(f"{tunnel_url.rstrip('/')}/system_stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tunnel is working! ComfyUI version: {data.get('system', {}).get('comfyui_version', 'unknown')}")
        else:
            print(f"❌ Tunnel not responding properly (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to tunnel: {e}")
        return False
    
    # Register tunnel with Railway app
    print(f"📡 Registering tunnel with Railway app...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-TUNNEL-SECRET': 'morphpas'  # Default secret
    }
    
    payload = {
        'url': tunnel_url
    }
    
    try:
        response = requests.post(
            f"{railway_url.rstrip('/')}/register-tunnel",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tunnel registered successfully!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   URL: {result.get('url', 'No URL')}")
            
            # Test GPU status endpoint
            print(f"🔍 Testing GPU status endpoint...")
            gpu_response = requests.get(f"{railway_url.rstrip('/')}/gpu-status", timeout=10)
            if gpu_response.status_code == 200:
                gpu_data = gpu_response.json()
                print(f"✅ GPU Status: {gpu_data.get('status', 'unknown')}")
                print(f"   Available: {gpu_data.get('available', False)}")
                print(f"   GPU Type: {gpu_data.get('gpu_type', 'unknown')}")
                print(f"   URL: {gpu_data.get('url', 'No URL')}")
            
            return True
            
        else:
            print(f"❌ Registration failed (status: {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration request failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint to see current GPU configuration"""
    railway_url = input("Enter your Railway app URL: ").strip()
    if not railway_url:
        print("❌ Railway URL is required")
        return
    
    try:
        response = requests.get(f"{railway_url.rstrip('/')}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"🏥 Health Check Results:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   GPU Type: {data.get('gpu_type', 'unknown')}")
            print(f"   GPU Status: {data.get('gpu_status', 'unknown')}")
            print(f"   GPU Info: {data.get('gpu_info', 'No info')}")
            print(f"   Local ComfyUI Enabled: {data.get('local_comfyui_enabled', False)}")
        else:
            print(f"❌ Health check failed (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🧪 Tunnel Registration Test")
    print("=" * 40)
    
    choice = input("Choose test:\n1. Register tunnel\n2. Check health\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = test_tunnel_registration()
        if success:
            print("\n🎉 Tunnel registration successful! Your Railway app should now use your local ComfyUI.")
        else:
            print("\n❌ Tunnel registration failed. Check the errors above.")
    elif choice == "2":
        test_health_endpoint()
    else:
        print("❌ Invalid choice")
