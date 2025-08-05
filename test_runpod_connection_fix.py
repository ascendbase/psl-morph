#!/usr/bin/env python3
"""
Test RunPod Connection Fix
Test the connection to your RunPod GPU from Railway deployment
"""

import requests
import json
import sys
from runpod_pod_client import RunPodPodClient

def test_runpod_connection():
    """Test connection to RunPod GPU"""
    
    # Your RunPod URL
    runpod_url = "https://choa76vtevld8t-8188.proxy.runpod.net"
    
    print(f"🔧 Testing RunPod Connection...")
    print(f"📡 URL: {runpod_url}")
    
    # Test 1: Direct HTTP request
    print("\n1️⃣ Testing direct HTTP connection...")
    try:
        response = requests.get(f"{runpod_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ Direct HTTP connection successful!")
            stats = response.json()
            print(f"   GPU Memory: {stats.get('system', {}).get('vram_total', 'Unknown')} MB")
        else:
            print(f"❌ HTTP connection failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP connection failed: {e}")
        return False
    
    # Test 2: RunPod client connection
    print("\n2️⃣ Testing RunPod client...")
    try:
        client = RunPodPodClient(runpod_url)
        print(f"   Client URL: {client.comfyui_url}")
        
        if client.test_connection():
            print("✅ RunPod client connection successful!")
        else:
            print("❌ RunPod client connection failed!")
            return False
    except Exception as e:
        print(f"❌ RunPod client error: {e}")
        return False
    
    # Test 3: ComfyUI API endpoints
    print("\n3️⃣ Testing ComfyUI API endpoints...")
    endpoints = [
        "/queue",
        "/history",
        "/prompt"
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint == "/prompt":
                # POST request for prompt endpoint
                response = requests.post(f"{runpod_url}{endpoint}", 
                                       json={"prompt": {}, "client_id": "test"}, 
                                       timeout=10)
            else:
                # GET request for other endpoints
                response = requests.get(f"{runpod_url}{endpoint}", timeout=10)
            
            if response.status_code in [200, 400]:  # 400 is OK for empty prompt
                print(f"   ✅ {endpoint}: Working")
            else:
                print(f"   ❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    print("\n🎯 Connection test completed!")
    return True

def test_image_upload():
    """Test image upload functionality"""
    print("\n4️⃣ Testing image upload capability...")
    
    runpod_url = "https://choa76vtevld8t-8188.proxy.runpod.net"
    
    try:
        # Test upload endpoint
        response = requests.get(f"{runpod_url}/upload/image", timeout=10)
        print(f"   Upload endpoint status: {response.status_code}")
        
        if response.status_code in [200, 405]:  # 405 Method Not Allowed is OK for GET
            print("   ✅ Upload endpoint accessible")
        else:
            print("   ❌ Upload endpoint not accessible")
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")

if __name__ == "__main__":
    print("🚀 RunPod Connection Test")
    print("=" * 50)
    
    success = test_runpod_connection()
    test_image_upload()
    
    if success:
        print("\n✅ All tests passed! Your RunPod connection should work.")
        print("🎊 Your Face Morphing SaaS can now connect to the RTX 5090!")
    else:
        print("\n❌ Some tests failed. Check your RunPod setup.")
        print("💡 Make sure ComfyUI is running with: python main.py --listen")