#!/usr/bin/env python3
"""
Test script to verify FaceDetailer workflow compatibility with ComfyUI API
"""

import json
import requests
import sys
import os

def test_facedetailer_workflow():
    """Test the FaceDetailer workflow with ComfyUI API"""
    
    # Load the workflow
    try:
        with open('comfyui_workflows/workflow_facedetailer.json', 'r') as f:
            workflow = json.load(f)
        print("✅ Successfully loaded FaceDetailer workflow")
    except Exception as e:
        print(f"❌ Failed to load workflow: {e}")
        return False
    
    # Test ComfyUI connection
    try:
        response = requests.get('http://127.0.0.1:8188/system_stats', timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI is running and accessible")
        else:
            print(f"⚠️  ComfyUI responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to ComfyUI: {e}")
        print("Make sure ComfyUI is running with --api flag")
        return False
    
    # Test workflow validation (dry run)
    try:
        # Prepare test payload
        test_payload = {
            "prompt": workflow,
            "client_id": "test_client"
        }
        
        # Try to validate the workflow structure
        print("🔍 Testing workflow structure...")
        
        # Check required nodes exist
        required_nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for node_id in required_nodes:
            if node_id not in workflow:
                print(f"❌ Missing required node: {node_id}")
                return False
        
        print("✅ All required nodes present")
        
        # Check node connections
        face_detailer_node = workflow.get("8")
        if not face_detailer_node:
            print("❌ FaceDetailer node (8) not found")
            return False
        
        if face_detailer_node.get("class_type") != "FaceDetailer":
            print("❌ Node 8 is not FaceDetailer class")
            return False
        
        print("✅ FaceDetailer node structure looks correct")
        
        # Test the actual API call (this will fail if extensions are missing)
        print("🚀 Testing actual API call...")
        response = requests.post(
            'http://127.0.0.1:8188/prompt',
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow accepted by ComfyUI API")
            print(f"   Prompt ID: {result.get('prompt_id', 'N/A')}")
            return True
        else:
            print(f"❌ API rejected workflow: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {error_detail}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")
        return False

def check_required_extensions():
    """Check if required ComfyUI extensions are installed"""
    print("\n🔍 Checking required extensions...")
    
    required_extensions = [
        "ComfyUI-Impact-Pack",  # For FaceDetailer
        "ComfyUI_UltralyticsDetectorProvider",  # For face detection
        "ComfyUI_Segment_Anything"  # For SAM
    ]
    
    # This is a basic check - in practice you'd need to check ComfyUI's extension directory
    print("ℹ️  Required extensions for FaceDetailer workflow:")
    for ext in required_extensions:
        print(f"   - {ext}")
    
    print("\nTo install missing extensions:")
    print("1. Open ComfyUI Manager")
    print("2. Search for and install the extensions listed above")
    print("3. Restart ComfyUI")

if __name__ == "__main__":
    print("Testing FaceDetailer Workflow Compatibility")
    print("=" * 50)
    
    success = test_facedetailer_workflow()
    
    if not success:
        check_required_extensions()
        print("\n💡 If the workflow fails:")
        print("1. Make sure all required extensions are installed")
        print("2. Check that your ComfyUI has the latest Impact Pack")
        print("3. Verify face detection models are downloaded")
        print("4. Try running the workflow manually in ComfyUI first")
    else:
        print("\n🎉 FaceDetailer workflow is ready to use!")
    
    sys.exit(0 if success else 1)