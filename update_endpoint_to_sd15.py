"""
Quick script to update RunPod endpoint to SD1.5 compatible image
This avoids waiting for Docker build and gets you working immediately
"""

import requests
import json
import os
from dotenv import load_dotenv

def update_endpoint_to_sd15():
    """Update endpoint to use SD1.5 compatible Docker image"""
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT_ID in .env file")
        return False
    
    # RunPod API endpoint for updating serverless endpoint
    url = f"https://api.runpod.ai/graphql"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # GraphQL mutation to update endpoint
    mutation = """
    mutation updateServerlessEndpoint($input: UpdateEndpointInput!) {
        updateEndpoint(input: $input) {
            id
            name
            dockerImage
        }
    }
    """
    
    # Update to SD1.5 compatible image
    variables = {
        "input": {
            "id": endpoint_id,
            "dockerImage": "runpod/worker-comfy:dev-cuda12.1.0"
        }
    }
    
    payload = {
        "query": mutation,
        "variables": variables
    }
    
    try:
        print(f"🔄 Updating endpoint {endpoint_id} to SD1.5 compatible image...")
        print(f"📦 New Docker image: runpod/worker-comfy:dev-cuda12.1.0")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'errors' in result:
                print(f"❌ GraphQL errors: {result['errors']}")
                return False
            
            if 'data' in result and result['data']['updateEndpoint']:
                endpoint_info = result['data']['updateEndpoint']
                print(f"✅ Endpoint updated successfully!")
                print(f"📋 Endpoint ID: {endpoint_info['id']}")
                print(f"📛 Name: {endpoint_info['name']}")
                print(f"🐳 Docker Image: {endpoint_info['dockerImage']}")
                print(f"")
                print(f"⏳ Endpoint is restarting... This takes 2-3 minutes")
                print(f"")
                print(f"🎯 Next steps:")
                print(f"1. Wait 2-3 minutes for restart")
                print(f"2. Test with: python runpod_sd15_client.py")
                print(f"3. Upload your models if needed")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating endpoint: {e}")
        return False

def check_endpoint_status():
    """Check current endpoint status"""
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing API credentials")
        return
    
    url = f"https://api.runpod.ai/graphql"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    query = """
    query getEndpoint($id: String!) {
        endpoint(id: $id) {
            id
            name
            dockerImage
            status
        }
    }
    """
    
    variables = {"id": endpoint_id}
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and result['data']['endpoint']:
                endpoint = result['data']['endpoint']
                print(f"📋 Current Endpoint Status:")
                print(f"   ID: {endpoint['id']}")
                print(f"   Name: {endpoint['name']}")
                print(f"   Docker Image: {endpoint['dockerImage']}")
                print(f"   Status: {endpoint['status']}")
                return endpoint
            else:
                print(f"❌ Endpoint not found or error: {result}")
                return None
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking endpoint: {e}")
        return None

if __name__ == "__main__":
    print("🚀 RunPod Endpoint SD1.5 Updater")
    print("=" * 50)
    
    # Check current status
    print("📊 Checking current endpoint status...")
    current_endpoint = check_endpoint_status()
    
    if current_endpoint:
        current_image = current_endpoint.get('dockerImage', '')
        
        if 'flux' in current_image.lower():
            print(f"")
            print(f"🎯 Current image is FLUX-based: {current_image}")
            print(f"🔄 This needs to be updated for SD1.5 models")
            print(f"")
            
            # Update to SD1.5
            success = update_endpoint_to_sd15()
            
            if success:
                print(f"")
                print(f"🎉 SUCCESS! Your endpoint is now SD1.5 compatible")
                print(f"")
                print(f"📝 What this means:")
                print(f"   ✅ Supports Stable Diffusion 1.5 models")
                print(f"   ✅ Compatible with your Real Dream base model")
                print(f"   ✅ Compatible with your Chad LoRA")
                print(f"   ✅ Ready for face morphing workflows")
                
        elif 'comfy' in current_image.lower() and 'dev' in current_image.lower():
            print(f"")
            print(f"✅ Current image is already SD1.5 compatible: {current_image}")
            print(f"🎯 You can proceed with testing your models")
            
        else:
            print(f"")
            print(f"⚠️  Unknown image type: {current_image}")
            print(f"🔄 Updating to known SD1.5 compatible image...")
            update_endpoint_to_sd15()
    
    print(f"")
    print(f"🧪 Next step: Test with your models")
    print(f"   python runpod_sd15_client.py")
