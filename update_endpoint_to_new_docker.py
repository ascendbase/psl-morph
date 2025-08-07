#!/usr/bin/env python3

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_runpod_endpoint():
    """Update RunPod serverless endpoint to use new Docker image"""
    
    # Get credentials from environment
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key:
        print("❌ RUNPOD_API_KEY not found in .env file")
        return False
        
    if not endpoint_id:
        print("❌ RUNPOD_ENDPOINT_ID not found in .env file")
        return False
    
    print(f"🔄 Updating endpoint {endpoint_id} to use new Docker image...")
    
    # New Docker image configuration
    new_config = {
        "name": "Face Morphing ComfyUI",
        "image": "ascendbase/face-morphing-comfyui:latest",
        "ports": "8188/http",
        "containerDiskInGb": 20,
        "volumeInGb": 0,
        "env": {},
        "startupTimeoutInSeconds": 300,
        "idleTimeoutInSeconds": 5,
        "scalerType": "QUEUE_DELAY",
        "scalerSettings": {
            "queueDelayTarget": 1,
            "maxWorkers": 3,
            "minWorkers": 0
        },
        "networkVolumeId": None,
        "locations": {
            "US": True,
            "EU": True,
            "AS": True
        },
        "gpuIds": "AMPERE_16,AMPERE_24,AMPERE_40,AMPERE_48,AMPERE_80,ADA_24"
    }
    
    # Update endpoint
    url = f"https://api.runpod.ai/graphql"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # GraphQL mutation to update endpoint
    mutation = """
    mutation updateEndpoint($input: EndpointUpdateInput!) {
        updateEndpoint(input: $input) {
            id
            name
            image
            ports
        }
    }
    """
    
    variables = {
        "input": {
            "endpointId": endpoint_id,
            **new_config
        }
    }
    
    payload = {
        "query": mutation,
        "variables": variables
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if "errors" in result:
            print(f"❌ GraphQL errors: {result['errors']}")
            return False
            
        if "data" in result and result["data"]["updateEndpoint"]:
            endpoint_data = result["data"]["updateEndpoint"]
            print(f"✅ Endpoint updated successfully!")
            print(f"   ID: {endpoint_data['id']}")
            print(f"   Name: {endpoint_data['name']}")
            print(f"   Image: {endpoint_data['image']}")
            print(f"   Ports: {endpoint_data['ports']}")
            print(f"\n🎯 Your endpoint is now using the new Docker image!")
            print(f"   Test with: python runpod_sd15_client.py")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False

def test_endpoint():
    """Test if the endpoint is working"""
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    api_key = os.getenv('RUNPOD_API_KEY')
    
    if not endpoint_id or not api_key:
        print("❌ Missing endpoint ID or API key")
        return False
    
    print(f"\n🧪 Testing endpoint {endpoint_id}...")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/health"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint is healthy and ready!")
            return True
        else:
            print(f"⚠️ Endpoint status: {response.status_code}")
            print("   It may still be starting up...")
            return False
    except Exception as e:
        print(f"⚠️ Health check failed: {e}")
        print("   This is normal if the endpoint is still starting up")
        return False

if __name__ == "__main__":
    print("🚀 Updating RunPod Serverless Endpoint to New Docker Image")
    print("=" * 60)
    
    if update_runpod_endpoint():
        print("\n" + "=" * 60)
        test_endpoint()
        print("\n🎉 Update complete! Your endpoint is ready to use.")
    else:
        print("\n❌ Update failed. Please check your configuration.")
