#!/usr/bin/env python3
"""
Simple test to verify tunnel detection is working
"""

import requests
import time
from cloudflare_tunnel_detector import tunnel_detector, get_dynamic_comfyui_url

def test_tunnel_detection():
    """Test the tunnel detection system"""
    print("🔍 Testing Cloudflare Tunnel Detection")
    print("=" * 50)
    
    # Test current detection
    url = get_dynamic_comfyui_url()
    print(f"Current URL: {url}")
    
    # Get detailed info
    info = tunnel_detector.get_tunnel_info()
    print(f"Status: {info['status']}")
    print(f"Message: {info['message']}")
    
    if info['status'] == 'connected':
        print(f"✅ Tunnel detected: {info['url']}")
        print(f"ComfyUI Version: {info.get('comfyui_version', 'unknown')}")
        print(f"GPU Devices: {len(info.get('devices', []))} detected")
        return True
    else:
        print(f"❌ No tunnel detected - using fallback: {url}")
        print("\nTo test with tunnel:")
        print("1. Start ComfyUI: python main.py --listen --port 8188")
        print("2. Start tunnel: cloudflared tunnel --url http://localhost:8188")
        print("3. Run this test again")
        return False

def test_specific_url(url):
    """Test a specific tunnel URL"""
    print(f"\n🔗 Testing specific URL: {url}")
    try:
        response = requests.get(f"{url}/system_stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URL is working!")
            print(f"ComfyUI Version: {data.get('system', {}).get('comfyui_version', 'unknown')}")
            return True
        else:
            print(f"❌ URL returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test current detection
    success = test_tunnel_detection()
    
    # If you have a specific tunnel URL to test, uncomment and modify this:
    # test_specific_url("https://your-tunnel-url.trycloudflare.com")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Tunnel detection is working!")
    else:
        print("⏳ Waiting for tunnel to be started...")
