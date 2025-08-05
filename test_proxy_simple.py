#!/usr/bin/env python3
"""
Simple test for RunPod proxy URLs
"""

import requests

def test_proxy():
    # Based on your pod ID from ComfyUI log
    pod_id = "00a7cc10019e"
    
    urls = [
        f"https://{pod_id}-8188.proxy.runpod.net",
        f"https://8188-{pod_id}.proxy.runpod.net",
        f"http://{pod_id}-8188.proxy.runpod.net",
        f"http://8188-{pod_id}.proxy.runpod.net",
    ]
    
    print("Testing RunPod Proxy URLs...")
    print("=" * 30)
    
    for url in urls:
        print(f"Testing: {url}")
        try:
            response = requests.get(f"{url}/system_stats", timeout=5)
            if response.status_code == 200:
                print("SUCCESS! Found working URL")
                print(f"URL: {url}")
                return url
            else:
                print(f"Failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"Failed: {str(e)[:50]}...")
        print()
    
    print("No proxy URLs work.")
    print("You need to use SSH tunnel or check RunPod dashboard for HTTP endpoints.")
    return None

if __name__ == "__main__":
    working_url = test_proxy()
    if working_url:
        print(f"\nUpdate .env with: {working_url}")