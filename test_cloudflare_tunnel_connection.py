#!/usr/bin/env python3
"""
Test connection to ComfyUI via Cloudflare tunnel
"""

import requests
import json
from config import LOCAL_COMFYUI_URL

def test_cloudflare_tunnel():
    """Test connection to ComfyUI via Cloudflare tunnel"""
    print(f"Testing connection to: {LOCAL_COMFYUI_URL}")
    
    try:
        # Test basic connection
        print("1. Testing basic connection...")
        response = requests.get(f"{LOCAL_COMFYUI_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Basic connection successful!")
        else:
            print(f"   ❌ Basic connection failed: {response.status_code}")
            return False
        
        # Test system stats endpoint
        print("2. Testing system stats endpoint...")
        response = requests.get(f"{LOCAL_COMFYUI_URL}/system_stats", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ System stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"   ❌ System stats failed: {response.status_code}")
        
        # Test queue endpoint
        print("3. Testing queue endpoint...")
        response = requests.get(f"{LOCAL_COMFYUI_URL}/queue", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            queue = response.json()
            print(f"   ✅ Queue status: {len(queue.get('queue_running', []))} running, {len(queue.get('queue_pending', []))} pending")
        else:
            print(f"   ❌ Queue check failed: {response.status_code}")
        
        # Test history endpoint
        print("4. Testing history endpoint...")
        response = requests.get(f"{LOCAL_COMFYUI_URL}/history", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ History endpoint accessible")
        else:
            print(f"   ❌ History endpoint failed: {response.status_code}")
        
        print("\n🎉 Cloudflare tunnel connection test completed!")
        print(f"Your ComfyUI is accessible at: {LOCAL_COMFYUI_URL}")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure your Cloudflare tunnel is running and ComfyUI is accessible")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error: {e}")
        print("The connection is taking too long - check your tunnel")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Cloudflare Tunnel Connection to ComfyUI")
    print("=" * 50)
    success = test_cloudflare_tunnel()
    
    if success:
        print("\n✅ SUCCESS: Your Railway app can now connect to your local ComfyUI!")
        print("The 'I need more money' message should disappear once Railway redeploys.")
    else:
        print("\n❌ FAILED: Connection issues detected.")
        print("Please check that:")
        print("1. ComfyUI is running locally on port 8188")
        print("2. Cloudflare tunnel is active")
        print("3. The tunnel URL matches the one in config.py")
