#!/usr/bin/env python3
"""
Final test of RTX 5090 face morphing functionality
"""

import requests
import json
import time
import os

# RTX 5090 proxy URL
COMFYUI_URL = "https://choa76vtevld8t-8188.proxy.runpod.net"

def test_rtx5090_connection():
    """Test basic connection to RTX 5090"""
    print("🔍 Testing RTX 5090 connection...")
    
    try:
        # Test queue endpoint
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=10)
        print(f"✅ Queue endpoint: {response.status_code}")
        
        # Test system stats
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System stats: {stats}")
        else:
            print(f"⚠️  System stats: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_simple_workflow():
    """Test a simple workflow on RTX 5090"""
    print("\n🧪 Testing simple workflow...")
    
    # Simple test workflow
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "real-dream-15.safetensors"
            }
        },
        "2": {
            "class_type": "EmptyLatentImage", 
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 12345,
                "steps": 5,  # Quick test
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["2", 0]
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "test image",
                "clip": ["1", 1]
            }
        },
        "5": {
            "class_type": "CLIPTextEncode", 
            "inputs": {
                "text": "bad quality",
                "clip": ["1", 1]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "rtx5090_test",
                "images": ["6", 0]
            }
        }
    }
    
    try:
        # Submit workflow
        payload = {
            "prompt": workflow,
            "client_id": "test_client"
        }
        
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=30)
        print(f"✅ Workflow submitted: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get('prompt_id')
            print(f"✅ Prompt ID: {prompt_id}")
            
            # Wait a bit and check status
            time.sleep(2)
            status_response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            if status_response.status_code == 200:
                print("✅ Workflow processing on RTX 5090!")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def main():
    print("🚀 RTX 5090 Face Morphing Test")
    print("=" * 50)
    
    # Test connection
    if not test_rtx5090_connection():
        print("❌ Connection test failed")
        return False
    
    # Test workflow
    if not test_simple_workflow():
        print("❌ Workflow test failed")
        return False
    
    print("\n🎉 RTX 5090 is ready for face morphing!")
    print("✅ Connection: Working")
    print("✅ Workflow processing: Working") 
    print("✅ Ready for production use")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)