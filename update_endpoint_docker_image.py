"""
Update RunPod endpoint to use your custom Docker image with Real Dream + Chad LoRA
Run this after GitHub Actions completes building your image
"""

import requests
import json
import os
from dotenv import load_dotenv

def update_endpoint_docker_image():
    """Update RunPod endpoint to use custom Docker image"""
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT_ID in .env file")
        return False
    
    # Your custom Docker image
    custom_image = "ascendbase/face-morphing-comfyui:latest"
    
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
    
    variables = {
        "input": {
            "id": endpoint_id,
            "dockerImage": custom_image
        }
    }
    
    payload = {
        "query": mutation,
        "variables": variables
    }
    
    try:
        print(f"🔄 Updating endpoint {endpoint_id} to custom Docker image...")
        print(f"📦 New Docker image: {custom_image}")
        print(f"🎯 This image includes:")
        print(f"   ✅ ComfyUI with SD1.5 support")
        print(f"   ✅ Real Dream base model")
        print(f"   ✅ Chad LoRA")
        print(f"   ✅ Face morphing capabilities")
        print(f"")
        
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
                print(f"⏳ Endpoint is restarting with your custom image...")
                print(f"   This takes 2-3 minutes for first time (downloading image)")
                print(f"   Subsequent starts will be faster (image cached)")
                print(f"")
                print(f"🎯 Next steps:")
                print(f"1. Wait 2-3 minutes for restart")
                print(f"2. Test with: python runpod_sd15_client.py")
                print(f"3. Your Real Dream + Chad LoRA models are ready!")
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

def check_docker_image_exists():
    """Check if the Docker image exists on Docker Hub"""
    
    image_name = "ascendbase/face-morphing-comfyui"
    
    try:
        # Check Docker Hub API
        url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/latest"
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ Docker image found: {image_name}:latest")
            return True
        elif response.status_code == 404:
            print(f"❌ Docker image not found: {image_name}:latest")
            print(f"")
            print(f"🔍 Possible reasons:")
            print(f"   1. GitHub Actions build is still running")
            print(f"   2. Build failed - check GitHub Actions tab")
            print(f"   3. Docker Hub credentials not set in GitHub secrets")
            print(f"")
            print(f"📋 To check:")
            print(f"   1. Go to: https://github.com/ascendbase/psl-morph/actions")
            print(f"   2. Look for 'Build and Push Docker Image' workflow")
            print(f"   3. Check if it completed successfully")
            return False
        else:
            print(f"⚠️  Unexpected response from Docker Hub: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Docker image: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RunPod Endpoint Docker Image Updater")
    print("=" * 50)
    
    # First check if the Docker image exists
    print("🔍 Checking if custom Docker image is available...")
    
    if check_docker_image_exists():
        print(f"")
        print("🎯 Docker image is ready! Updating RunPod endpoint...")
        
        success = update_endpoint_docker_image()
        
        if success:
            print(f"")
            print(f"🎉 SUCCESS! Your RunPod endpoint now uses your custom image")
            print(f"")
            print(f"📝 What this means:")
            print(f"   ✅ Your endpoint has Real Dream + Chad LoRA built-in")
            print(f"   ✅ No need to upload models separately")
            print(f"   ✅ Face morphing ready to use")
            print(f"   ✅ Serverless GPU with your specific models")
            print(f"")
            print(f"🧪 Test your deployment:")
            print(f"   python runpod_sd15_client.py")
        else:
            print(f"")
            print(f"❌ Failed to update endpoint. Check your .env file:")
            print(f"   RUNPOD_API_KEY=your_api_key")
            print(f"   RUNPOD_ENDPOINT_ID=your_endpoint_id")
    else:
        print(f"")
        print(f"⏳ Docker image not ready yet. Please:")
        print(f"   1. Check GitHub Actions build status")
        print(f"   2. Wait for build to complete")
        print(f"   3. Run this script again")
        print(f"")
        print(f"🔗 GitHub Actions: https://github.com/ascendbase/psl-morph/actions")
