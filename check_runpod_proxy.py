#!/usr/bin/env python3
"""
Check if RunPod provides HTTP proxy URLs for ComfyUI
"""

import requests
import time

def check_proxy_urls():
    """Check common RunPod proxy URL patterns"""
    
    # Common RunPod proxy patterns
    pod_id = "00a7cc10019e"  # From your ComfyUI log
    
    proxy_urls = [
        f"https://{pod_id}-8188.proxy.runpod.net",
        f"https://8188-{pod_id}.proxy.runpod.net", 
        f"http://{pod_id}-8188.proxy.runpod.net",
        f"http://8188-{pod_id}.proxy.runpod.net",
        # Alternative patterns
        f"https://{pod_id}.proxy.runpod.net:8188",
        f"http://{pod_id}.proxy.runpod.net:8188",
    ]
    
    print("Checking RunPod HTTP Proxy URLs...")
    print("=" * 40)
    
    for url in proxy_urls:
        print(f"Testing: {url}")
        try:
            response = requests.get(f"{url}/system_stats", timeout=10)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {url}")
                print(f"Response: {response.json()}")
                return url
            else:
                print(f"❌ HTTP {response.status_code}")
        except requests.exceptions.SSLError:
            print("❌ SSL Error")
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error")
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()
    
    print("❌ No working proxy URL found")
    print("\nAlternatives:")
    print("1. Check your RunPod dashboard for HTTP endpoints")
    print("2. Look for 'Public URL' or 'HTTP Proxy' in pod settings")
    print("3. Use SSH tunnel (if SSH key works)")
    
    return None

if __name__ == "__main__":
    working_url = check_proxy_urls()
    
    if working_url:
        print(f"\n🎉 Found working URL!")
        print(f"Update your .env file:")
        
        if working_url.startswith('https://'):
            url_part = working_url.replace('https://', '')
            print(f"RUNPOD_POD_URL={url_part}")
            print(f"RUNPOD_POD_PORT=443")
        else:
            url_part = working_url.replace('http://', '')
            if ':' in url_part:
                host, port = url_part.split(':')
                print(f"RUNPOD_POD_URL={host}")
                print(f"RUNPOD_POD_PORT={port}")
            else:
                print(f"RUNPOD_POD_URL={url_part}")
                print(f"RUNPOD_POD_PORT=80")