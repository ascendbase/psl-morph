"""
Test script for custom nose feature transformation
"""

import os
import json
import requests
import time
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_custom_nose_workflow():
    """Test the custom nose workflow directly"""
    
    # Test image path (you can replace with your own test image)
    test_image_path = "test_image.jpg"
    
    # Check if test image exists
    if not os.path.exists(test_image_path):
        logger.error(f"Test image not found: {test_image_path}")
        logger.info("Please place a test image named 'test_image.jpg' in the current directory")
        return False
    
    try:
        # Test local ComfyUI client with custom nose feature
        from local_comfyui_client import LocalComfyUIClient
        
        # Initialize client
        client = LocalComfyUIClient()
        
        # Test connection
        if not client.test_connection():
            logger.error("Cannot connect to ComfyUI")
            return False
        
        logger.info("✅ Connected to ComfyUI successfully")
        
        # Test custom nose feature generation
        logger.info("🚀 Starting custom nose feature generation...")
        
        prompt_id = client.generate_image_with_features(
            image_path=test_image_path,
            selected_features=['nose'],
            denoise_strength=0.33
        )
        
        if not prompt_id:
            logger.error("❌ Failed to start generation")
            return False
        
        logger.info(f"✅ Generation started with prompt ID: {prompt_id}")
        
        # Poll for completion
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = client.get_job_status(prompt_id)
            logger.info(f"Status: {status}")
            
            if status == "COMPLETED":
                logger.info("🎉 Generation completed!")
                
                # Get the result
                result_data = client.get_job_output(prompt_id)
                if result_data:
                    # Save result
                    result_filename = f"custom_nose_result_{int(time.time())}.png"
                    with open(result_filename, 'wb') as f:
                        f.write(result_data)
                    
                    logger.info(f"✅ Result saved as: {result_filename}")
                    
                    # Verify the result image
                    try:
                        with Image.open(result_filename) as img:
                            logger.info(f"📸 Result image size: {img.size}")
                            logger.info(f"📸 Result image mode: {img.mode}")
                    except Exception as e:
                        logger.error(f"❌ Error opening result image: {e}")
                    
                    return True
                else:
                    logger.error("❌ Failed to get result data")
                    return False
            
            elif status == "FAILED":
                logger.error("❌ Generation failed")
                return False
            
            else:
                logger.info("⏳ Generation in progress...")
                time.sleep(5)
        
        logger.error("⏰ Generation timed out")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

def test_workflow_file():
    """Test that the custom nose workflow file is valid"""
    
    workflow_path = "comfyui_workflows/workflow_custom_nose.json"
    
    if not os.path.exists(workflow_path):
        logger.error(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        logger.info("✅ Workflow file is valid JSON")
        
        # Check required nodes
        required_nodes = ["5", "6", "8", "9"]  # LoadImage, FaceAnalysis, FaceDetailer, SaveImage
        
        for node_id in required_nodes:
            if node_id not in workflow:
                logger.error(f"❌ Missing required node: {node_id}")
                return False
        
        logger.info("✅ All required nodes present")
        
        # Check node configurations
        if workflow["6"]["inputs"]["area"] != "nose":
            logger.error("❌ FaceAnalysis node not configured for nose")
            return False
        
        if workflow["8"]["inputs"]["denoise"] != 0.33:
            logger.error("❌ FaceDetailer node not configured with 0.33 denoise")
            return False
        
        logger.info("✅ Workflow configuration is correct")
        logger.info(f"   - Area: {workflow['6']['inputs']['area']}")
        logger.info(f"   - Denoise: {workflow['8']['inputs']['denoise']}")
        logger.info(f"   - Grow: {workflow['6']['inputs']['grow']}")
        logger.info(f"   - Blur: {workflow['6']['inputs']['blur']}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in workflow file: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error reading workflow file: {e}")
        return False

def test_web_interface():
    """Test the web interface for custom features"""
    
    # This would require a running Flask app
    # For now, just check that the template has been updated
    
    template_path = "templates/index.html"
    
    if not os.path.exists(template_path):
        logger.error(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for custom features elements
        required_elements = [
            'id="modeSection"',
            'id="customFeaturesSection"',
            'data-feature="nose"',
            'transform_mode',
            'selected_features'
        ]
        
        for element in required_elements:
            if element not in content:
                logger.error(f"❌ Missing element in template: {element}")
                return False
        
        logger.info("✅ Web interface template updated correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading template file: {e}")
        return False

def main():
    """Run all tests"""
    
    logger.info("🧪 Testing Custom Nose Feature Implementation")
    logger.info("=" * 50)
    
    tests = [
        ("Workflow File Validation", test_workflow_file),
        ("Web Interface Template", test_web_interface),
        ("Custom Nose Generation", test_custom_nose_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.info(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Custom nose feature is ready!")
    else:
        logger.info("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
