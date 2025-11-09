#!/usr/bin/env python3
"""
Test script to verify tunnel connection is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloudflare_tunnel_detector import get_dynamic_comfyui_url, tunnel_detector
from local_comfyui_client import LocalComfyUIClient
from tunnel_registry import get_tunnel_url
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tunnel_connection():
    """Test the complete tunnel connection system"""
    print("🔧 Testing Tunnel Connection System")
    print("=" * 50)
    
    # 1. Check tunnel registry
    print("\n1. Checking tunnel registry...")
    reg_url = get_tunnel_url()
    if reg_url:
        print(f"✅ Registry URL found: {reg_url}")
    else:
        print("❌ No URL in registry")
    
    # 2. Test dynamic URL detection
    print("\n2. Testing dynamic URL detection...")
    dynamic_url = get_dynamic_comfyui_url()
    print(f"🔍 Dynamic URL: {dynamic_url}")
    
    # 3. Test tunnel detector
    print("\n3. Testing tunnel detector...")
    info = tunnel_detector.get_tunnel_info()
    print(f"Status: {info['status']}")
    print(f"URL: {info.get('url', 'None')}")
    print(f"Message: {info['message']}")
    
    # 4. Test LocalComfyUIClient
    print("\n4. Testing LocalComfyUIClient...")
    client = LocalComfyUIClient()
    print(f"Client URL: {client.base_url}")
    
    connection_test = client.test_connection()
    if connection_test:
        print("✅ LocalComfyUIClient connection successful!")
    else:
        print("❌ LocalComfyUIClient connection failed")
    
    # 5. Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Registry URL: {reg_url or 'None'}")
    print(f"Dynamic URL: {dynamic_url}")
    print(f"Client URL: {client.base_url}")
    print(f"Connection: {'✅ SUCCESS' if connection_test else '❌ FAILED'}")
    
    if connection_test:
        print("\n🎉 Tunnel connection system is working!")
        print("Your Railway app should now be able to connect to local ComfyUI")
    else:
        print("\n⚠️  Tunnel connection failed")
        print("Make sure:")
        print("1. ComfyUI is running locally on port 8188")
        print("2. Cloudflare tunnel is active")
        print("3. Tunnel URL has been registered via webhook")
    
    return connection_test

if __name__ == "__main__":
    test_tunnel_connection()
