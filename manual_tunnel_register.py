#!/usr/bin/env python3
"""
Manual tunnel registration tool
Use this when automatic detection fails
"""

import requests
import sys

def register_tunnel_url(url, webhook="https://psl-morph-production.up.railway.app/register-tunnel", secret="morphpas"):
    """Manually register a tunnel URL"""
    headers = {"X-TUNNEL-SECRET": secret}
    payload = {"url": url}
    
    try:
        print(f"Registering tunnel URL: {url}")
        print(f"Webhook: {webhook}")
        
        response = requests.post(webhook, json=payload, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Tunnel URL registered successfully!")
            return True
        else:
            print("❌ Failed to register tunnel URL")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Manual Tunnel URL Registration")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("\nPlease check your Cloudflare tunnel window for a URL like:")
        print("  https://xxxxx-xxxxx-xxxxx.trycloudflare.com")
        print()
        url = input("Enter the tunnel URL: ").strip()
    
    if not url:
        print("No URL provided")
        return
    
    if not url.startswith('https://'):
        print("URL should start with https://")
        return
    
    if 'trycloudflare.com' not in url:
        print("URL should be a trycloudflare.com URL")
        return
    
    success = register_tunnel_url(url)
    
    if success:
        print("\n🎉 Success! Your Railway app can now connect to your local ComfyUI")
        print("You can now test image transformations on your web app")
    else:
        print("\n❌ Registration failed. Please check the URL and try again")

if __name__ == "__main__":
    main()
