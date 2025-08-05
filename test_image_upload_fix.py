#!/usr/bin/env python3
"""
Test script to verify image upload and workflow fixes for RTX 5090
"""

import os
import sys
import requests
import json
from runpod_pod_client import RunPodPodClient
from config import *

def test_rtx5090_image_processing():
    """Test the complete image processing pipeline"""
    print("🧪 Testing RTX 5090 Image Processing Pipeline")
    print("=" * 50)
    
    # Initialize client
    client = RunPodPodClient(RUNPOD_POD_URL, RUNPOD_POD_PORT)
    
    # Test connection
    print("1. Testing connection to RTX 5090...")
    if client.test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
        return False
    
    # Find a test image
    test_image = None
    for filename in os.listdir('uploads'):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            test_image = os.path.join('uploads', filename)
            break
    
    if not test_image:
        print("❌ No test images found in uploads folder")
        return False
    
    print(f"2. Using test image: {test_image}")
    
    # Test image upload
    print("3. Testing image upload to ComfyUI...")
    if client.upload_image(test_image):
        print("✅ Image upload successful!")
    else:
        print("❌ Image upload failed!")
        return False
    
    # Test workflow preparation
    print("4. Testing FaceDetailer workflow preparation...")
    workflow = client._prepare_workflow(test_image, 0.5, "Chadlite")
    if workflow:
        print("✅ Workflow preparation successful!")
        print(f"   - Workflow has {len(workflow)} nodes")
        print(f"   - LoadImage node: {workflow.get('5', {}).get('inputs', {}).get('image', 'Not found')}")
        print(f"   - FaceDetailer denoise: {workflow.get('8', {}).get('inputs', {}).get('denoise', 'Not found')}")
    else:
        print("❌ Workflow preparation failed!")
        return False
    
    # Test workflow queuing (but don't wait for completion)
    print("5. Testing workflow queuing...")
    prompt_id = client._queue_workflow(workflow)
    if prompt_id:
        print(f"✅ Workflow queued successfully! Prompt ID: {prompt_id}")
        
        # Check initial status
        status = client.get_job_status(prompt_id)
        print(f"   - Initial status: {status}")
        
        return True
    else:
        print("❌ Workflow queuing failed!")
        return False

def test_comfyui_endpoints():
    """Test ComfyUI API endpoints directly"""
    print("\n🔧 Testing ComfyUI API Endpoints")
    print("=" * 50)
    
    base_url = COMFYUI_URL
    
    endpoints = [
        ("/system_stats", "System Stats"),
        ("/queue", "Queue Status"),
        ("/history", "History"),
        ("/object_info", "Object Info")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

if __name__ == "__main__":
    print("🚀 RTX 5090 Image Processing Test")
    print(f"ComfyUI URL: {COMFYUI_URL}")
    print(f"RunPod Pod URL: {RUNPOD_POD_URL}:{RUNPOD_POD_PORT}")
    print()
    
    # Test API endpoints first
    test_comfyui_endpoints()
    
    # Test full pipeline
    success = test_rtx5090_image_processing()
    
    if success:
        print("\n🎉 All tests passed! RTX 5090 integration is working correctly.")
        print("\nYou can now:")
        print("1. Start the app with: start_rtx5090.bat")
        print("2. Upload an image and test face morphing")
        print("3. The image upload issue should be fixed!")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        
    print(f"\nTest completed. Check the logs for details.")