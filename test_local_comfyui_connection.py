#!/usr/bin/env python3
"""
Test script to verify local ComfyUI connection and workflow
"""

import requests
import json
import time
import sys

def test_comfyui_connection():
    """Test if ComfyUI is running and accessible"""
    print("🔍 Testing ComfyUI Connection...")
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:8188", timeout=10)
        if response.status_code == 200:
            print("✅ ComfyUI is running on localhost:8188")
            return True
        else:
            print(f"❌ ComfyUI returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ComfyUI on localhost:8188")
        print("   Make sure ComfyUI is running!")
        return False
    except Exception as e:
        print(f"❌ Error connecting to ComfyUI: {e}")
        return False

def test_workflow_upload():
    """Test if we can load the FaceDetailer workflow"""
    print("\n🔍 Testing Workflow Upload...")
    
    try:
        # Load the workflow
        with open("comfyui_workflows/workflow_facedetailer.json", "r") as f:
            workflow = json.load(f)
        
        print("✅ FaceDetailer workflow loaded successfully")
        print(f"   Workflow has {len(workflow)} nodes")
        
        # Check for key nodes
        key_nodes = ["CheckpointLoaderSimple", "FaceDetailer", "SaveImage"]
        found_nodes = []
        
        for node_id, node_data in workflow.items():
            if node_data.get("class_type") in key_nodes:
                found_nodes.append(node_data.get("class_type"))
        
        print(f"   Found key nodes: {found_nodes}")
        
        if "FaceDetailer" in found_nodes:
            print("✅ FaceDetailer node found in workflow")
        else:
            print("⚠️  FaceDetailer node not found - make sure it's installed")
        
        return True
        
    except FileNotFoundError:
        print("❌ Workflow file not found: comfyui_workflows/workflow_facedetailer.json")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in workflow file")
        return False
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        return False

def test_api_endpoints():
    """Test ComfyUI API endpoints"""
    print("\n🔍 Testing ComfyUI API Endpoints...")
    
    endpoints = [
        ("/queue", "Queue endpoint"),
        ("/history", "History endpoint"),
        ("/system_stats", "System stats endpoint")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8188{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} working")
            else:
                print(f"⚠️  {description} returned {response.status_code}")
        except Exception as e:
            print(f"❌ {description} failed: {e}")

def main():
    print("=" * 50)
    print("   LOCAL COMFYUI CONNECTION TEST")
    print("=" * 50)
    
    # Test connection
    if not test_comfyui_connection():
        print("\n❌ ComfyUI connection failed!")
        print("\nTroubleshooting:")
        print("1. Make sure ComfyUI is running")
        print("2. Check if port 8188 is accessible")
        print("3. Try opening http://localhost:8188 in your browser")
        sys.exit(1)
    
    # Test workflow
    workflow_ok = test_workflow_upload()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    if workflow_ok:
        print("🎉 LOCAL COMFYUI IS READY!")
        print("\nNext steps:")
        print("1. Set up tunnel (ngrok or Cloudflare)")
        print("2. Configure Railway environment variables")
        print("3. Deploy and test!")
    else:
        print("⚠️  ComfyUI is running but workflow needs attention")
        print("\nPlease check:")
        print("1. FaceDetailer nodes are installed")
        print("2. Required models are in place")
        print("3. Workflow file is valid")
    print("=" * 50)

if __name__ == "__main__":
    main()
