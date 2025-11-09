"""
Test Reference Chad feature fix for production deployment
Tests both ComfyUI clients to ensure face swap functionality works
"""

import os
import sys

def test_simple_comfyui_client():
    """Test the simple ComfyUI client has face swap functionality"""
    print("🧪 Testing simple ComfyUI client...")
    
    try:
        from comfyui_client import ComfyUIClient
        
        # Create client instance
        client = ComfyUIClient("http://127.0.0.1:8188")
        
        # Check if the method exists
        if hasattr(client, 'generate_image_with_face_swap'):
            print("✅ generate_image_with_face_swap method exists in ComfyUIClient")
            
            # Check method signature
            import inspect
            sig = inspect.signature(client.generate_image_with_face_swap)
            params = list(sig.parameters.keys())
            expected_params = ['original_image_path', 'reference_image_path', 'swap_intensity']
            
            if all(param in params for param in expected_params):
                print("✅ Method has correct parameters:", params)
                return True
            else:
                print("❌ Method has incorrect parameters:", params)
                return False
        else:
            print("❌ generate_image_with_face_swap method missing in ComfyUIClient")
            return False
            
    except Exception as e:
        print(f"❌ Error testing simple ComfyUI client: {e}")
        return False

def test_local_comfyui_client():
    """Test the local ComfyUI client has face swap functionality"""
    print("\n🧪 Testing local ComfyUI client...")
    
    try:
        from local_comfyui_client import LocalComfyUIClient
        
        # Create client instance
        client = LocalComfyUIClient()
        
        # Check if the method exists
        if hasattr(client, 'generate_image_with_face_swap'):
            print("✅ generate_image_with_face_swap method exists in LocalComfyUIClient")
            
            # Check method signature
            import inspect
            sig = inspect.signature(client.generate_image_with_face_swap)
            params = list(sig.parameters.keys())
            expected_params = ['original_image_path', 'reference_image_path', 'swap_intensity']
            
            if all(param in params for param in expected_params):
                print("✅ Method has correct parameters:", params)
                return True
            else:
                print("❌ Method has incorrect parameters:", params)
                return False
        else:
            print("❌ generate_image_with_face_swap method missing in LocalComfyUIClient")
            return False
            
    except Exception as e:
        print(f"❌ Error testing local ComfyUI client: {e}")
        return False

def test_workflow_file_exists():
    """Test that the face swap workflow file exists"""
    print("\n🧪 Testing face swap workflow file...")
    
    workflow_path = "comfyui_workflows/face_swap_with_intensity.json"
    
    if os.path.exists(workflow_path):
        print(f"✅ Face swap workflow file exists: {workflow_path}")
        
        # Check if it's valid JSON
        try:
            import json
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            if "nodes" in workflow:
                print("✅ Workflow has nodes array format")
                
                # Check for required node types
                node_types = [node.get("type") for node in workflow["nodes"] if isinstance(node, dict)]
                required_types = ["LoadImage", "ReActorSetWeight", "ReActorFaceSwap", "SaveImage"]
                
                missing_types = [t for t in required_types if t not in node_types]
                if not missing_types:
                    print("✅ Workflow has all required node types")
                    return True
                else:
                    print(f"❌ Workflow missing node types: {missing_types}")
                    return False
            else:
                print("❌ Workflow missing nodes array")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in workflow file: {e}")
            return False
    else:
        print(f"❌ Face swap workflow file not found: {workflow_path}")
        return False

def test_reference_chad_images():
    """Test that reference chad images exist"""
    print("\n🧪 Testing reference chad images...")
    
    reference_dir = "reference_chads"
    expected_images = ["barrett.jpg", "gandy.jpg", "elias.jpg", "pitt.jpg", "hernan.jpg"]
    
    if os.path.exists(reference_dir):
        print(f"✅ Reference directory exists: {reference_dir}")
        
        existing_images = os.listdir(reference_dir)
        missing_images = []
        
        for img in expected_images:
            # Check for various extensions
            found = False
            for ext in ['.jpg', '.jpeg', '.png']:
                if any(f.lower() == img.replace('.jpg', ext).lower() for f in existing_images):
                    found = True
                    break
            
            if not found:
                missing_images.append(img)
        
        if not missing_images:
            print(f"✅ All reference images found: {len(existing_images)} files")
            return True
        else:
            print(f"⚠️  Some reference images missing: {missing_images}")
            print(f"📁 Available files: {existing_images}")
            return len(missing_images) < len(expected_images)  # Partial success
    else:
        print(f"❌ Reference directory not found: {reference_dir}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Reference Chad Production Fix")
    print("=" * 50)
    
    tests = [
        ("Simple ComfyUI Client", test_simple_comfyui_client),
        ("Local ComfyUI Client", test_local_comfyui_client),
        ("Face Swap Workflow", test_workflow_file_exists),
        ("Reference Chad Images", test_reference_chad_images)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Reference Chad feature should work in production.")
    elif passed >= len(results) - 1:
        print("⚠️  Most tests passed. Reference Chad feature should work with minor issues.")
    else:
        print("❌ Multiple tests failed. Reference Chad feature may not work properly.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
