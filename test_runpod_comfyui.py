"""
Test RunPod ComfyUI Setup
Verifies the RunPod endpoint is working correctly
"""

import os
import sys
from runpod_comfyui_client import RunPodComfyUIClient

def test_runpod_setup():
    """Test RunPod ComfyUI endpoint"""
    
    print("=" * 60)
    print("RunPod ComfyUI Setup Test")
    print("=" * 60)
    print()
    
    # Load credentials
    API_KEY = os.getenv("RUNPOD_API_KEY")
    ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID")
    
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        print("❌ ERROR: RUNPOD_API_KEY not set in .env file")
        print("Please add your RunPod API key to .env")
        return False
    
    if not ENDPOINT_ID or ENDPOINT_ID == "YOUR_ENDPOINT_ID":
        print("❌ ERROR: RUNPOD_ENDPOINT_ID not set in .env file")
        print("Please add your RunPod endpoint ID to .env")
        return False
    
    print(f"✓ API Key loaded: {API_KEY[:10]}...")
    print(f"✓ Endpoint ID: {ENDPOINT_ID}")
    print()
    
    # Create client
    print("Creating RunPod client...")
    client = RunPodComfyUIClient(API_KEY, ENDPOINT_ID)
    print("✓ Client created")
    print()
    
    # Test 1: Health Check
    print("-" * 60)
    print("Test 1: Health Check")
    print("-" * 60)
    health = client.health_check()
    
    if health["status"] == "healthy":
        print("✓ Endpoint is healthy")
        print(f"  Details: {health.get('details', {})}")
    else:
        print(f"❌ Endpoint health check failed: {health}")
        print()
        print("Troubleshooting:")
        print("1. Verify endpoint is deployed in RunPod console")
        print("2. Check endpoint ID is correct")
        print("3. Verify Docker image exists on DockerHub")
        return False
    
    print()
    
    # Test 2: Check workflow file
    print("-" * 60)
    print("Test 2: Workflow File Check")
    print("-" * 60)
    
    workflow_path = "comfyui_workflows/workflow_facedetailer.json"
    if os.path.exists(workflow_path):
        print(f"✓ Workflow file found: {workflow_path}")
    else:
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    print()
    
    # Test 3: Simple workflow execution (without image)
    print("-" * 60)
    print("Test 3: Simple Workflow Test")
    print("-" * 60)
    print("Note: This test will charge a small amount (~$0.02)")
    print()
    
    test_image = None
    
    # Look for a test image
    test_paths = [
        "betaface_test_images/test1.jpg",
        "uploads/test.jpg",
        "test.jpg"
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if test_image:
        print(f"✓ Test image found: {test_image}")
        print()
        print("Running FaceDetailer workflow...")
        print("This may take 30-60 seconds on first run (cold start)...")
        
        try:
            result = client.run_facedetailer(
                input_image=test_image,
                prompt="chad, male model, perfect face",
                denoise=0.50,
                steps=20
            )
            
            if result["status"] == "success":
                print()
                print("✓ Workflow executed successfully!")
                print(f"  Execution time: {result.get('execution_time', 'N/A')} seconds")
                print(f"  Output: {result.get('output', {})}")
                print()
                print("=" * 60)
                print("ALL TESTS PASSED! ✓")
                print("=" * 60)
                print()
                print("Your RunPod ComfyUI setup is working correctly!")
                return True
            else:
                print()
                print(f"❌ Workflow execution failed")
                print(f"  Error: {result.get('message', 'Unknown error')}")
                print(f"  Details: {result.get('details', {})}")
                print()
                print("Troubleshooting:")
                print("1. Check RunPod endpoint logs")
                print("2. Verify models are included in Docker image")
                print("3. Check workflow JSON is valid")
                return False
                
        except Exception as e:
            print()
            print(f"❌ Error running workflow: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("⚠ No test image found")
        print("Skipping workflow execution test")
        print()
        print("To fully test, add an image to:")
        for path in test_paths:
            print(f"  - {path}")
        print()
        print("=" * 60)
        print("PARTIAL SUCCESS ✓")
        print("=" * 60)
        print()
        print("Endpoint is healthy but workflow test skipped.")
        print("Add a test image and run again for full verification.")
        return True

if __name__ == "__main__":
    success = test_runpod_setup()
    sys.exit(0 if success else 1)
