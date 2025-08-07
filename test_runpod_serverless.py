#!/usr/bin/env python3
"""
Test script for RunPod Serverless endpoint
Run this after deploying to verify the connection works
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_runpod_serverless():
    """Test the RunPod serverless endpoint"""
    
    # Get configuration from environment
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    api_key = os.getenv('RUNPOD_API_KEY')
    
    if not endpoint_id or not api_key:
        print("❌ Missing RunPod configuration!")
        print("Please set RUNPOD_ENDPOINT_ID and RUNPOD_API_KEY in your .env file")
        return False
    
    print(f"🧪 Testing RunPod Serverless Endpoint: {endpoint_id}")
    print("=" * 50)
    
    # RunPod serverless URL
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload to check if ComfyUI is running
    test_payload = {
        "input": {
            "workflow": {
                "1": {
                    "inputs": {},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {
                        "title": "Load Checkpoint"
                    }
                }
            }
        }
    }
    
    try:
        print("📡 Sending test request...")
        start_time = time.time()
        
        response = requests.post(url, headers=headers, json=test_payload, timeout=60)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RunPod Serverless endpoint is working!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (60 seconds)")
        print("💡 This might be normal for cold starts - try again")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    print("=" * 50)
    
    required_vars = [
        'RUNPOD_ENDPOINT_ID',
        'RUNPOD_API_KEY',
        'USE_CLOUD_GPU',
        'USE_RUNPOD_POD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var in ['RUNPOD_API_KEY']:
                print(f"✅ {var}: {'*' * 20} (hidden)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the RunPod configuration")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 RunPod Serverless Test")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed!")
        exit(1)
    
    print("\n" + "=" * 50)
    
    # Test the endpoint
    if test_runpod_serverless():
        print("\n🎉 All tests passed! Your RunPod serverless endpoint is ready.")
    else:
        print("\n❌ Tests failed. Please check your configuration and try again.")
        print("\n💡 Troubleshooting tips:")
        print("1. Verify your endpoint ID and API key are correct")
        print("2. Check that the endpoint is deployed and active in RunPod dashboard")
        print("3. Ensure the Docker image was pushed successfully to Docker Hub")
        print("4. Try again in a few minutes (cold start can take time)")
