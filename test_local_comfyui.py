"""
Test script for Local ComfyUI integration
Tests the new local_comfyui_client.py with the workflow_facedetailer.json workflow
"""

import os
import sys
import time
import logging
from PIL import Image

# Add current directory to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_local_comfyui():
    """Test the local ComfyUI client"""
    try:
        # Import the local ComfyUI client
        from local_comfyui_client import LocalComfyUIClient
        
        # Initialize client
        client = LocalComfyUIClient(
            base_url="http://127.0.0.1:8188",
            workflow_path="comfyui_workflows/workflow_facedetailer.json",
            timeout=300
        )
        
        print("=" * 60)
        print("LOCAL COMFYUI INTEGRATION TEST")
        print("=" * 60)
        
        # Test 1: Connection test
        print("\n1. Testing ComfyUI connection...")
        if client.test_connection():
            print("✅ ComfyUI connection successful!")
        else:
            print("❌ ComfyUI connection failed!")
            print("   Make sure ComfyUI is running on http://127.0.0.1:8188")
            return False
        
        # Test 2: Workflow template loading
        print("\n2. Testing workflow template loading...")
        if client.workflow_template:
            print("✅ Workflow template loaded successfully!")
            print(f"   Workflow has {len(client.workflow_template)} nodes")
        else:
            print("❌ Failed to load workflow template!")
            return False
        
        # Test 3: Check if test image exists
        print("\n3. Checking for test image...")
        test_image_path = "test_image.png"
        if not os.path.exists(test_image_path):
            print(f"❌ Test image not found: {test_image_path}")
            print("   Please place a test image named 'test_image.png' in the current directory")
            return False
        else:
            print(f"✅ Test image found: {test_image_path}")
        
        # Test 4: Image upload
        print("\n4. Testing image upload to ComfyUI...")
        if client.upload_image(test_image_path):
            print("✅ Image uploaded successfully!")
        else:
            print("❌ Image upload failed!")
            return False
        
        # Test 5: Workflow preparation
        print("\n5. Testing workflow preparation...")
        workflow = client._prepare_workflow(test_image_path, 0.15, "tier2")
        if workflow:
            print("✅ Workflow prepared successfully!")
            print(f"   Input image: {workflow['5']['inputs']['image']}")
            print(f"   Denoise strength: {workflow['8']['inputs']['denoise']}")
            print(f"   Seed: {workflow['8']['inputs']['seed']}")
        else:
            print("❌ Workflow preparation failed!")
            return False
        
        # Test 6: Full generation test (optional - only if user confirms)
        print("\n6. Full generation test...")
        response = input("Do you want to run a full generation test? This will use your GPU. (y/N): ")
        if response.lower() == 'y':
            print("   Starting generation...")
            prompt_id = client.generate_image(
                image_path=test_image_path,
                preset_name="tier2",
                denoise_strength=0.15
            )
            
            if prompt_id:
                print(f"✅ Generation started! Prompt ID: {prompt_id}")
                
                # Wait for completion
                print("   Waiting for completion...")
                max_wait = 120  # 2 minutes max
                wait_time = 0
                
                while wait_time < max_wait:
                    status = client.get_job_status(prompt_id)
                    print(f"   Status: {status}")
                    
                    if status == "COMPLETED":
                        print("✅ Generation completed!")
                        
                        # Get output
                        output_data = client.get_job_output(prompt_id)
                        if output_data:
                            output_path = f"test_output_{int(time.time())}.png"
                            with open(output_path, 'wb') as f:
                                f.write(output_data)
                            print(f"✅ Output saved to: {output_path}")
                        else:
                            print("❌ Failed to get output image")
                        break
                    elif status == "FAILED":
                        print("❌ Generation failed!")
                        break
                    
                    time.sleep(5)
                    wait_time += 5
                
                if wait_time >= max_wait:
                    print("⏰ Generation timed out")
            else:
                print("❌ Failed to start generation!")
        else:
            print("   Skipped full generation test")
        
        print("\n" + "=" * 60)
        print("LOCAL COMFYUI INTEGRATION TEST COMPLETED")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.exception("Test failed")
        return False

def create_test_image():
    """Create a simple test image if none exists"""
    test_image_path = "test_image.png"
    if not os.path.exists(test_image_path):
        print(f"Creating test image: {test_image_path}")
        # Create a simple 512x512 test image
        img = Image.new('RGB', (512, 512), color='lightblue')
        img.save(test_image_path)
        print(f"✅ Test image created: {test_image_path}")

if __name__ == "__main__":
    print("Local ComfyUI Integration Test")
    print("This script tests the integration with your local ComfyUI instance")
    print()
    
    # Create test image if needed
    create_test_image()
    
    # Run the test
    success = test_local_comfyui()
    
    if success:
        print("\n🎉 All tests passed! Your local ComfyUI integration is working correctly.")
        print("\nNext steps:")
        print("1. Make sure ComfyUI is running when you start your web app")
        print("2. Start your web app with: python app.py")
        print("3. The app will now use your local GPU instead of cloud services!")
    else:
        print("\n❌ Some tests failed. Please check the errors above and fix them.")
        print("\nCommon issues:")
        print("- ComfyUI not running (start it with: python main.py)")
        print("- Wrong ComfyUI URL (check if it's running on http://127.0.0.1:8188)")
        print("- Missing workflow file (check comfyui_workflows/workflow_facedetailer.json)")
        print("- Missing required ComfyUI nodes (install FaceDetailer, Impact Pack, etc.)")
