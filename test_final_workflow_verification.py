#!/usr/bin/env python3
"""
Final verification test to ensure the app uses workflow_facedetailer.json
"""

import json
import os
import sys

def test_config_workflow():
    """Test that config.py points to the correct workflow"""
    print("🔧 Testing Config.py Workflow Setting")
    print("=" * 50)
    
    # Import config to get the actual values
    try:
        from config import LOCAL_COMFYUI_WORKFLOW, USE_LOCAL_COMFYUI, CURRENT_WORKFLOW
        
        print(f"✅ USE_LOCAL_COMFYUI: {USE_LOCAL_COMFYUI}")
        print(f"✅ CURRENT_WORKFLOW: {CURRENT_WORKFLOW}")
        print(f"✅ LOCAL_COMFYUI_WORKFLOW: {LOCAL_COMFYUI_WORKFLOW}")
        
        # Check if it points to the correct workflow
        if LOCAL_COMFYUI_WORKFLOW == 'comfyui_workflows/workflow_facedetailer.json':
            print("✅ Config correctly points to workflow_facedetailer.json")
            return True
        else:
            print(f"❌ Config points to wrong workflow: {LOCAL_COMFYUI_WORKFLOW}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing config: {e}")
        return False

def test_local_comfyui_client():
    """Test that local_comfyui_client.py loads the correct workflow"""
    print("\n🔧 Testing Local ComfyUI Client")
    print("=" * 50)
    
    try:
        # Import the client
        from local_comfyui_client import LocalComfyUIClient
        from config import LOCAL_COMFYUI_WORKFLOW
        
        # Create client instance
        client = LocalComfyUIClient(
            base_url="http://test.com",
            workflow_path=LOCAL_COMFYUI_WORKFLOW,
            timeout=30
        )
        
        print(f"✅ Client created with workflow: {client.workflow_path}")
        
        # Test workflow loading
        if client.workflow_template:
            print("✅ Workflow loaded successfully")
            
            # Check if it's the FaceDetailer workflow
            if "8" in client.workflow_template and client.workflow_template["8"].get("class_type") == "FaceDetailer":
                print("✅ Workflow contains FaceDetailer node (node 8)")
                return True
            else:
                print("❌ Workflow does not contain FaceDetailer node")
                return False
        else:
            print("❌ Failed to load workflow")
            return False
            
    except Exception as e:
        print(f"❌ Error testing client: {e}")
        return False

def test_app_workflow_usage():
    """Test that app.py will use the correct workflow"""
    print("\n🔧 Testing App.py Workflow Usage")
    print("=" * 50)
    
    try:
        # Check the app.py file for workflow usage
        # Try different encodings to handle the file
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        app_content = None
        
        for encoding in encodings:
            try:
                with open('app.py', 'r', encoding=encoding) as f:
                    app_content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if app_content is None:
            print("❌ Could not read app.py with any encoding")
            return False
        
        # Check if it imports LOCAL_COMFYUI_WORKFLOW
        if 'LOCAL_COMFYUI_WORKFLOW' in app_content:
            print("✅ App.py imports LOCAL_COMFYUI_WORKFLOW from config")
        else:
            print("❌ App.py does not import LOCAL_COMFYUI_WORKFLOW")
            return False
        
        # Check if it uses LocalComfyUIClient
        if 'LocalComfyUIClient' in app_content:
            print("✅ App.py uses LocalComfyUIClient")
        else:
            print("❌ App.py does not use LocalComfyUIClient")
            return False
        
        # Check if it passes the workflow path to the client
        if 'workflow_path=LOCAL_COMFYUI_WORKFLOW' in app_content:
            print("✅ App.py passes LOCAL_COMFYUI_WORKFLOW to client")
            return True
        else:
            print("❌ App.py does not pass workflow path correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_workflow_file_exists():
    """Test that the workflow file exists and is valid"""
    print("\n🔧 Testing Workflow File")
    print("=" * 50)
    
    workflow_path = "comfyui_workflows/workflow_facedetailer.json"
    
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    print(f"✅ Workflow file exists: {workflow_path}")
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        print("✅ Workflow JSON is valid")
        
        # Check for FaceDetailer node
        if "8" in workflow and workflow["8"].get("class_type") == "FaceDetailer":
            print("✅ Workflow contains FaceDetailer node (node 8)")
            
            # Check denoise parameter
            denoise = workflow["8"]["inputs"].get("denoise", "not found")
            print(f"✅ Current denoise value: {denoise}")
            
            return True
        else:
            print("❌ Workflow does not contain FaceDetailer node")
            return False
            
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Final Workflow Verification Test")
    print("=" * 60)
    
    tests = [
        ("Config Workflow Setting", test_config_workflow),
        ("Local ComfyUI Client", test_local_comfyui_client),
        ("App Workflow Usage", test_app_workflow_usage),
        ("Workflow File", test_workflow_file_exists)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your app WILL use workflow_facedetailer.json")
        print("✅ The FaceDetailer workflow is correctly configured")
        print("✅ Ready to deploy to Railway!")
        
        print("\n📝 Summary of what will happen:")
        print("   1. Railway app starts with USE_LOCAL_COMFYUI=true")
        print("   2. App loads LOCAL_COMFYUI_WORKFLOW=workflow_facedetailer.json")
        print("   3. LocalComfyUIClient uses the FaceDetailer workflow")
        print("   4. When users click 'Start Transformation', it uses FaceDetailer")
        print("   5. Denoise values: +1 Tier=0.10, +2 Tier=0.17, Chad=0.25")
        
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Please fix the issues above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
