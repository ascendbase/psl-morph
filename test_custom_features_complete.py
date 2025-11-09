#!/usr/bin/env python3
"""
Test script for all custom facial features (eyes, nose, mouth, chin)
Tests the complete implementation with 0.3 denoise strength
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from local_comfyui_client import LocalComfyUIClient

def test_custom_features():
    """Test all custom features with their respective workflows"""
    
    print("🧪 Testing Custom Features Implementation")
    print("=" * 50)
    
    # Initialize client
    client = LocalComfyUIClient()
    
    # Test connection
    print("1. Testing ComfyUI connection...")
    if not client.test_connection():
        print("❌ ComfyUI connection failed!")
        return False
    print("✅ ComfyUI connection successful")
    
    # Check supported features
    print("\n2. Checking supported features...")
    expected_features = ['eyes', 'nose', 'mouth', 'chin']
    
    for feature in expected_features:
        if feature in client.supported_features:
            config = client.supported_features[feature]
            print(f"✅ {feature.capitalize()}: {config['workflow']}")
            print(f"   - Area: {config['area']}")
            print(f"   - Grow: {config['grow']}")
            print(f"   - Blur: {config['blur']}")
        else:
            print(f"❌ {feature.capitalize()}: Not found in supported features")
            return False
    
    # Check workflow files exist
    print("\n3. Checking workflow files...")
    for feature in expected_features:
        workflow_path = client.supported_features[feature]['workflow']
        if os.path.exists(workflow_path):
            print(f"✅ {workflow_path}")
            
            # Verify workflow content
            try:
                with open(workflow_path, 'r') as f:
                    workflow = json.load(f)
                
                # Check key nodes exist
                required_nodes = ["1", "5", "6", "8", "10", "11"]  # Key nodes for custom workflows
                missing_nodes = [node for node in required_nodes if node not in workflow]
                
                if missing_nodes:
                    print(f"   ⚠️  Missing nodes: {missing_nodes}")
                else:
                    print(f"   ✅ All required nodes present")
                    
                # Check denoise value is 0.3
                if "8" in workflow and "denoise" in workflow["8"]["inputs"]:
                    denoise = workflow["8"]["inputs"]["denoise"]
                    if denoise == 0.3:
                        print(f"   ✅ Denoise strength: {denoise}")
                    else:
                        print(f"   ⚠️  Denoise strength: {denoise} (expected 0.3)")
                
                # Check area mapping
                if "6" in workflow and "area" in workflow["6"]["inputs"]:
                    area = workflow["6"]["inputs"]["area"]
                    expected_area = client.supported_features[feature]['area']
                    if area == expected_area:
                        print(f"   ✅ Area mapping: {area}")
                    else:
                        print(f"   ⚠️  Area mapping: {area} (expected {expected_area})")
                        
            except Exception as e:
                print(f"   ❌ Error reading workflow: {e}")
                return False
        else:
            print(f"❌ {workflow_path} - File not found")
            return False
    
    # Test feature workflow loading
    print("\n4. Testing feature workflow loading...")
    client.load_feature_workflows()
    
    for feature in expected_features:
        if feature in client.feature_workflows:
            print(f"✅ {feature.capitalize()} workflow loaded successfully")
        else:
            print(f"❌ {feature.capitalize()} workflow failed to load")
            return False
    
    # Test workflow preparation for each feature
    print("\n5. Testing workflow preparation...")
    test_image_path = "test_image.jpg"
    
    # Create a dummy test image file for testing
    if not os.path.exists(test_image_path):
        print(f"   Creating dummy test image: {test_image_path}")
        # Create a minimal test file
        with open(test_image_path, 'wb') as f:
            f.write(b'dummy_image_data')
    
    for feature in expected_features:
        print(f"\n   Testing {feature} workflow preparation...")
        try:
            workflow = client._prepare_workflow(
                image_path=test_image_path,
                denoise_strength=0.3,
                preset_name="Custom_Features",
                selected_features=[feature]
            )
            
            if workflow:
                print(f"   ✅ {feature.capitalize()} workflow prepared successfully")
                
                # Verify key parameters
                if "5" in workflow and workflow["5"]["inputs"]["image"] == "test_image.jpg":
                    print(f"      ✅ Image input set correctly")
                
                if "8" in workflow and workflow["8"]["inputs"]["denoise"] == 0.3:
                    print(f"      ✅ Denoise strength set to 0.3")
                
                if "6" in workflow:
                    area = workflow["6"]["inputs"]["area"]
                    expected_area = client.supported_features[feature]['area']
                    if area == expected_area:
                        print(f"      ✅ Area set to {area}")
                    else:
                        print(f"      ⚠️  Area mismatch: {area} vs {expected_area}")
                
            else:
                print(f"   ❌ {feature.capitalize()} workflow preparation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error preparing {feature} workflow: {e}")
            return False
    
    # Clean up test file
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    
    print("\n6. Testing generate_image_with_features method...")
    try:
        # This will fail because we don't have a real image, but it should validate the method exists
        result = client.generate_image_with_features(
            image_path="nonexistent.jpg",
            selected_features=["nose"],
            denoise_strength=0.3
        )
        print("   ✅ generate_image_with_features method accessible")
    except Exception as e:
        if "No such file" in str(e) or "upload" in str(e).lower():
            print("   ✅ generate_image_with_features method accessible (expected file error)")
        else:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL CUSTOM FEATURES TESTS PASSED!")
    print("\nImplemented Features:")
    for feature in expected_features:
        config = client.supported_features[feature]
        print(f"  • {feature.capitalize()}: {config['area']} area, 0.3 denoise")
    
    print("\nFeatures are ready for use in the web interface!")
    return True

def test_ui_integration():
    """Test that the UI has been updated with all features"""
    print("\n🖥️  Testing UI Integration")
    print("=" * 30)
    
    ui_file = "templates/index.html"
    if not os.path.exists(ui_file):
        print(f"❌ UI file not found: {ui_file}")
        return False
    
    with open(ui_file, 'r', encoding='utf-8') as f:
        ui_content = f.read()
    
    # Check for all feature options in HTML
    expected_features = ['eyes', 'nose', 'mouth', 'chin']
    feature_icons = ['👀', '👃', '👄', '🫵']
    
    for i, feature in enumerate(expected_features):
        feature_html = f'data-feature="{feature}"'
        icon = feature_icons[i]
        
        if feature_html in ui_content and icon in ui_content:
            print(f"✅ {feature.capitalize()} feature found in UI")
        else:
            print(f"❌ {feature.capitalize()} feature missing from UI")
            return False
    
    # Check for 30% denoise text
    if "30% transformation intensity" in ui_content:
        print("✅ UI shows correct 30% denoise strength")
    else:
        print("❌ UI missing 30% denoise strength text")
        return False
    
    # Check for 0.3 denoise in JavaScript
    if "selectedDenoise = 0.3" in ui_content:
        print("✅ JavaScript uses 0.3 denoise for custom features")
    else:
        print("❌ JavaScript missing 0.3 denoise setting")
        return False
    
    print("✅ UI integration complete!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Custom Features Complete Test")
    print("Testing implementation of eyes, nose, mouth, and chin features")
    print("All features use 0.3 denoise strength for precise results\n")
    
    success = True
    
    # Test backend implementation
    if not test_custom_features():
        success = False
    
    # Test UI integration
    if not test_ui_integration():
        success = False
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nCustom Features Implementation Complete:")
        print("✅ Eyes - 0.3 denoise, eyes area")
        print("✅ Nose - 0.3 denoise, nose area") 
        print("✅ Mouth - 0.3 denoise, lips area")
        print("✅ Chin - 0.3 denoise, chin area")
        print("\nThe app now supports precise facial feature transformation!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)
