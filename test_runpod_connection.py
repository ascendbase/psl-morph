#!/usr/bin/env python3
"""
Quick RunPod Connection Diagnostic Tool
Tests different connection methods to find what works
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection_methods():
    """Test different ways to connect to the RunPod"""
    
    pod_ip = os.getenv('RUNPOD_POD_URL', '149.36.1.79')
    pod_port = os.getenv('RUNPOD_POD_PORT', '8188')
    
    print("RunPod Connection Diagnostic Tool")
    print("=" * 50)
    print(f"Pod IP: {pod_ip}")
    print(f"Pod Port: {pod_port}")
    print()
    
    # Test methods
    test_urls = [
        f"http://{pod_ip}:{pod_port}",
        f"https://{pod_ip}:{pod_port}",
        f"http://{pod_ip}:8188",
        f"https://{pod_ip}:8188",
    ]
    
    # If it looks like a proxy URL, test that too
    if '.proxy.runpod.net' in pod_ip:
        test_urls.extend([
            f"https://{pod_ip}",
            f"http://{pod_ip}",
        ])
    
    for url in test_urls:
        print(f"Testing: {url}")
        try:
            response = requests.get(f"{url}/system_stats", timeout=10)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {url}")
                print(f"   Response: {response.json()}")
                return url
            else:
                print(f"❌ HTTP {response.status_code}: {url}")
        except requests.exceptions.SSLError:
            print(f"❌ SSL Error: {url}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: {url}")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: {url}")
        except Exception as e:
            print(f"❌ Error: {url} - {e}")
        print()
    
    print("❌ No working connection found!")
    print()
    print("Troubleshooting steps:")
    print("1. Check if your RunPod is running")
    print("2. Verify ComfyUI is started with: python main.py --listen 0.0.0.0 --port 8188")
    print("3. Check RunPod dashboard for correct IP and port mapping")
    print("4. Try using RunPod's proxy URL if available")
    
    return None

if __name__ == "__main__":
    working_url = test_connection_methods()
    if working_url:
        print(f"\n🎉 Use this URL in your .env file:")
        print(f"RUNPOD_POD_URL={working_url.replace('http://', '').replace('https://', '').split(':')[0]}")
        if ':' in working_url.split('//')[1]:
            port = working_url.split(':')[-1]
            print(f"RUNPOD_POD_PORT={port}")