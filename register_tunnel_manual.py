#!/usr/bin/env python3
"""
Manual Tunnel Registration Script
Use this to manually register your Cloudflare tunnel URL with the Railway app
"""

import requests
import sys

def register_tunnel(tunnel_url, railway_url="https://psl-morph-production.up.railway.app"):
    """Register tunnel URL with the Railway app"""
    
    # Validate URL format
    if not tunnel_url.startswith('https://'):
        print("❌ Error: URL must start with https://")
        return False
    
    if 'trycloudflare.com' not in tunnel_url:
        print("❌ Error: URL must be a trycloudflare.com tunnel")
        return False
    
    print(f"🔄 Registering tunnel URL: {tunnel_url}")
    print(f"📡 Target Railway app: {railway_url}")
    
    try:
        # Test the tunnel URL first
        print("🧪 Testing tunnel connection...")
        test_response = requests.get(f"{tunnel_url.rstrip('/')}/system_stats", timeout=10)
        
        if test_response.status_code == 200:
            data = test_response.json()
            print(f"✅ Tunnel is working!")
            print(f"   ComfyUI Version: {data.get('system', {}).get('comfyui_version', 'Unknown')}")
            print(f"   GPU Devices: {len(data.get('devices', []))} detected")
        else:
            print(f"⚠️  Warning: Tunnel responded with status {test_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing tunnel: {e}")
        print("⚠️  Continuing with registration anyway...")
    
    try:
        # Register with Railway app
        print("📝 Registering with Railway app...")
        register_response = requests.post(
            f"{railway_url}/register-tunnel",
            headers={
                'Content-Type': 'application/json',
                'X-TUNNEL-SECRET': 'morphpas'
            },
            json={'url': tunnel_url},
            timeout=15
        )
        
        if register_response.status_code == 200:
            result = register_response.json()
            if result.get('success'):
                print("✅ Successfully registered tunnel URL!")
                print(f"   Message: {result.get('message', 'Registration complete')}")
                return True
            else:
                print(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Registration failed with status {register_response.status_code}")
            try:
                error_data = register_response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registering tunnel: {e}")
        return False

def main():
    print("🚀 Manual Tunnel Registration Tool")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Usage: python register_tunnel_manual.py <tunnel_url>")
        print("\nExample:")
        print("  python register_tunnel_manual.py https://abc-def-ghi.trycloudflare.com")
        print("\nSteps:")
        print("1. Start ComfyUI: python main.py --listen 0.0.0.0 --port 8188")
        print("2. Start tunnel: cloudflared tunnel --url http://127.0.0.1:8188")
        print("3. Copy the tunnel URL from the output")
        print("4. Run this script with the URL")
        sys.exit(1)
    
    tunnel_url = sys.argv[1].strip()
    
    # Clean up URL
    if tunnel_url.endswith('/'):
        tunnel_url = tunnel_url[:-1]
    
    print(f"🎯 Target tunnel URL: {tunnel_url}")
    
    success = register_tunnel(tunnel_url)
    
    if success:
        print("\n🎉 Registration complete!")
        print("✅ Your Railway app should now use your local ComfyUI")
        print("🔗 Test it at: https://psl-morph-production.up.railway.app/app")
    else:
        print("\n❌ Registration failed!")
        print("💡 Try:")
        print("   1. Check that ComfyUI is running on port 8188")
        print("   2. Check that the tunnel is active")
        print("   3. Verify the tunnel URL is correct")

if __name__ == "__main__":
    main()
