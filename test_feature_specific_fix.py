#!/usr/bin/env python3
"""
Test script to verify the feature-specific transformation fix
"""

import os
import sys
import logging
from local_comfyui_client import LocalComfyUIClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_feature_specific_workflow():
    """Test that feature-specific workflows are correctly configured"""
    
    print("🧪 Testing Feature-Specific Workflow Fix")
    print("=" * 50)
    
    # Initialize client
    client = LocalComfyUIClient()
    
    # Test each feature
    test_features = ['eyes', 'nose', 'lips', 'eyebrows', 'chin']
    
    for feature in test_features:
        print(f"\n🔍 Testing {feature} feature:")
        
        # Check if workflow is loaded
        if feature in client.feature_workflows:
            workflow = client.feature_workflows[feature]
            
            # Check FaceSegmentation node (node 6)
            if "6" in workflow:
                face_seg_node = workflow["6"]
                current_area = face_seg_node["inputs"].get("area", "NOT_SET")
                expected_area = client.supported_features[feature]["area"]
                
                print(f"  📄 Workflow loaded: ✅")
                print(f"  🎯 Current area: {current_area}")
                print(f"  🎯 Expected area: {expected_area}")
                
                if current_area == expected_area:
                    print(f"  ✅ Area configuration: CORRECT")
                else:
                    print(f"  ❌ Area configuration: MISMATCH")
                
                # Check other parameters
                grow = face_seg_node["inputs"].get("grow", "NOT_SET")
                blur = face_seg_node["inputs"].get("blur", "NOT_SET")
                print(f"  📏 Grow: {grow}")
                print(f"  🌫️  Blur: {blur}")
                
            else:
                print(f"  ❌ FaceSegmentation node (6) not found in workflow")
        else:
            print(f"  ❌ Workflow not loaded for {feature}")
    
    print(f"\n🔧 Testing dynamic parameter override:")
    
    # Test the _prepare_workflow method with a specific feature
    test_image_path = "test_image.png"  # Dummy path for testing
    
    # Create a dummy image file for testing
    if not os.path.exists(test_image_path):
        print(f"  📝 Creating dummy test image: {test_image_path}")
        with open(test_image_path, 'w') as f:
            f.write("dummy")
    
    try:
        # Test eyes feature
        workflow = client._prepare_workflow(
            image_path=test_image_path,
            denoise_strength=0.3,
            preset_name="Test",
            selected_features=['eyes']
        )
        
        if workflow and "6" in workflow:
            face_seg_node = workflow["6"]
            area = face_seg_node["inputs"].get("area")
            grow = face_seg_node["inputs"].get("grow")
            blur = face_seg_node["inputs"].get("blur")
            
            print(f"  🎯 Dynamic area override: {area}")
            print(f"  📏 Dynamic grow override: {grow}")
            print(f"  🌫️  Dynamic blur override: {blur}")
            
            expected_config = client.supported_features['eyes']
            if (area == expected_config['area'] and 
                grow == expected_config['grow'] and 
                blur == expected_config['blur']):
                print(f"  ✅ Dynamic parameter override: WORKING")
            else:
                print(f"  ❌ Dynamic parameter override: FAILED")
        else:
            print(f"  ❌ Failed to prepare workflow or FaceSegmentation node missing")
            
    except Exception as e:
        print(f"  ❌ Error testing dynamic override: {e}")
    
    # Clean up dummy file
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    
    print(f"\n🎉 Feature-specific workflow test completed!")
    print(f"💡 The fix ensures that when users select a specific feature,")
    print(f"   only that feature area will be transformed, not multiple areas.")

if __name__ == "__main__":
    test_feature_specific_workflow()
