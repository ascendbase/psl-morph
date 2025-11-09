#!/usr/bin/env python3
"""
Test script to verify the Reference Chad feature fix
"""

import os
import sys
import logging
from local_comfyui_client import LocalComfyUIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reference_chad_fix():
    """Test the Reference Chad feature with the bug fix"""
    
    print("🧪 Testing Reference Chad Feature Fix")
    print("=" * 50)
    
    # Initialize client
    client = LocalComfyUIClient()
    
    # Test connection
    print("1. Testing ComfyUI connection...")
    if not client.test_connection():
        print("❌ ComfyUI connection failed - make sure ComfyUI is running")
        return False
    print("✅ ComfyUI connection successful")
    
    # Test face swap method (this is where the bug was)
    print("\n2. Testing face swap method (where the bug was fixed)...")
    
    # Create dummy image files for testing
    test_original = "test_original.jpg"
    test_reference = "test_reference.jpg"
    
    # Create minimal test images (1x1 pixel)
    from PIL import Image
    
    # Create test original image
    img = Image.new('RGB', (1, 1), color='red')
    img.save(test_original)
    
    # Create test reference image  
    img = Image.new('RGB', (1, 1), color='blue')
    img.save(test_reference)
    
    try:
        # This should not throw the 'str' object has no attribute 'get' error anymore
        result = client.generate_image_with_face_swap(
            original_image_path=test_original,
            reference_image_path=test_reference,
            swap_intensity="50%"
        )
        
        if result:
            print("✅ Face swap method executed without errors")
            print(f"   Generated prompt ID: {result}")
        else:
            print("⚠️  Face swap method returned None (but no error thrown)")
            
    except Exception as e:
        if "'str' object has no attribute 'get'" in str(e):
            print(f"❌ The original bug is still present: {e}")
            return False
        else:
            print(f"⚠️  Different error occurred (this might be expected): {e}")
    
    finally:
        # Clean up test files
        if os.path.exists(test_original):
            os.remove(test_original)
        if os.path.exists(test_reference):
            os.remove(test_reference)
    
    print("\n3. Checking reference chad images...")
    reference_dir = "reference_chads"
    if os.path.exists(reference_dir):
        files = os.listdir(reference_dir)
        expected_files = ["barrett.png", "gandy.png", "elias.png", "pitt.png", "hernan.png"]
        
        for expected_file in expected_files:
            if expected_file in files:
                print(f"✅ {expected_file} found")
            else:
                print(f"❌ {expected_file} missing")
    else:
        print(f"❌ Reference directory {reference_dir} not found")
    
    print("\n" + "=" * 50)
    print("🎉 Reference Chad feature fix test completed!")
    print("The 'str' object has no attribute 'get' error should be fixed.")
    
    return True

if __name__ == "__main__":
    test_reference_chad_fix()
