#!/usr/bin/env python3
import json
import requests

def test_workflow():
    try:
        with open('comfyui_workflows/workflow_facedetailer.json', 'r') as f:
            workflow = json.load(f)
        print("OK: Loaded FaceDetailer workflow")
        
        # Use an existing uploaded image for testing
        import os
        upload_files = [f for f in os.listdir('uploads') if f.endswith(('.jpg', '.png', '.jpeg'))]
        if upload_files:
            test_image = upload_files[0]
            workflow["5"]["inputs"]["image"] = test_image
            print(f"OK: Using test image: {test_image}")
        else:
            print("WARNING: No test images found in uploads folder")
            
    except Exception as e:
        print(f"ERROR: Failed to load workflow: {e}")
        return False
    
    try:
        response = requests.get('http://127.0.0.1:8188/system_stats', timeout=5)
        if response.status_code == 200:
            print("OK: ComfyUI is running")
        else:
            print(f"ERROR: ComfyUI status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to ComfyUI: {e}")
        return False
    
    try:
        test_payload = {
            "prompt": workflow,
            "client_id": "test_client"
        }
        
        response = requests.post(
            'http://127.0.0.1:8188/prompt',
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"OK: Workflow accepted, prompt_id: {result.get('prompt_id', 'N/A')}")
            return True
        else:
            print(f"ERROR: API rejected workflow: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Details: {error_detail}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing FaceDetailer Workflow")
    print("=" * 30)
    success = test_workflow()
    print("=" * 30)
    if success:
        print("SUCCESS: FaceDetailer workflow is working!")
    else:
        print("FAILED: Check ComfyUI extensions and try again")