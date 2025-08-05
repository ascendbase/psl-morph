#!/usr/bin/env python3
"""
Simple connection test for RunPod ComfyUI
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    pod_url = os.getenv('RUNPOD_POD_URL', '149.36.1.79')
    pod_port = os.getenv('RUNPOD_POD_PORT', '8188')
    
    print("RunPod Connection Test")
    print("=" * 30)
    print(f"Testing: http://{pod_url}:{pod_port}")
    
    try:
        # Test system stats endpoint
        response = requests.get(f"http://{pod_url}:{pod_port}/system_stats", timeout=10)
        
        if response.status_code == 200:
            print("SUCCESS: Connected to ComfyUI!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"FAILED: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("FAILED: Connection refused")
        print("ComfyUI might not be accessible from outside the pod")
        return False
    except requests.exceptions.Timeout:
        print("FAILED: Connection timeout")
        return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\nYour RTX 5090 is ready!")
        print("You can now run: python app.py")
    else:
        print("\nConnection failed. ComfyUI is running but not accessible externally.")
        print("You may need to use SSH tunneling or check for HTTP proxy URLs.")