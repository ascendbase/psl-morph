#!/usr/bin/env python3
"""
Test the specific tunnel URL that's currently running
"""

import requests

def test_tunnel_url():
    tunnel_url = "https://keeping-za-volume-enclosed.trycloudflare.com"
    
    print(f"🔗 Testing tunnel: {tunnel_url}")
    print("=" * 60)
    
    try:
        # Test if ComfyUI is accessible
        response = requests.get(f"{tunnel_url}/system_stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Tunnel is working!")
            print(f"ComfyUI Version: {data.get('system', {}).get('comfyui_version', 'unknown')}")
            print(f"Devices: {len(data.get('devices', []))} GPU(s) detected")
            print(f"System: {data.get('system', {})}")
            return True
        else:
            print(f"❌ Tunnel responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tunnel_url()
    
    if success:
        print("\n🎉 Your tunnel is working perfectly!")
        print("Your Railway app will automatically detect this tunnel!")
    else:
        print("\n⚠️  Tunnel not responding - make sure ComfyUI is running")
