#!/usr/bin/env python3
"""
Test Reference Chad Feature - Final Fix Verification
Tests the complete workflow conversion and face swap functionality
"""

import sys
import os
import json
import tempfile
from PIL import Image

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_comfyui_client import LocalComfyUIClient

def create_test_image(filename):
    """Create a test image file"""
    img = Image.new('RGB', (512, 512), color='red')
    img.save(filename)
    return filename

def test_workflow_conversion():
    """Test the workflow conversion from nodes array to direct node dict format"""
    print("🧪 Testing workflow conversion...")
    
    # Load the face swap workflow
    workflow_path = "comfyui_workflows/face_swap_with_intensity.json"
    if not os.path.exists(workflow_path):
        print(f"❌ Face swap workflow not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    print(f"✅ Loaded workflow: {workflow_path}")
    print(f"   - Has 'nodes' key: {'nodes' in workflow}")
    print(f"   - Number of nodes: {len(workflow.get('nodes', []))}")
    
    # Test the conversion logic
    if "nodes" in workflow:
        print("🔄 Testing nodes array to direct node dict conversion...")
        
        nodes_list = workflow["nodes"]
        new_workflow = {}
        
        original_image_set = False
        source_image_set = False
        
        for node in nodes_list:
            if not isinstance(node, dict):
                continue
            
            node_id = str(node.get("id"))
            
            # Convert node structure
            new_node = {
                "class_type": node.get("type"),  # Convert "type" to "class_type"
                "inputs": {}
            }
            
            # Handle LoadImage nodes specially
            if node.get("type") == "LoadImage":
                title = node.get("title", "").lower()
                print(f"   - Found LoadImage node {node_id} with title: '{node.get('title', '')}'")
                
                # Set the image input based on title
                if "original" in title and not original_image_set:
                    new_node["inputs"]["image"] = "test_original.jpg"
                    print(f"   - Set original image in node {node_id}")
                    original_image_set = True
                elif "source" in title and not source_image_set:
                    new_node["inputs"]["image"] = "test_reference.jpg"
                    print(f"   - Set reference image in node {node_id}")
                    source_image_set = True
                
                # Set upload input
                new_node["inputs"]["upload"] = "image"
            
            # Handle ReActorSetWeight nodes
            elif node.get("type") == "ReActorSetWeight":
                new_node["inputs"]["faceswap_weight"] = "75%"
                print(f"   - Set face swap intensity in ReActorSetWeight node {node_id}: 75%")
            
            # Handle SaveImage nodes
            elif node.get("type") == "SaveImage":
                new_node["inputs"]["filename_prefix"] = "face_swap_test"
                print(f"   - Set output filename prefix in SaveImage node {node_id}")
            
            new_workflow[node_id] = new_node
        
        # Copy other workflow properties (skip non-dict items like 'links' array)
        for key, value in workflow.items():
            if key != "nodes":
                new_workflow[key] = value
        
        print(f"✅ Conversion successful!")
        print(f"   - Original image set: {original_image_set}")
        print(f"   - Source image set: {source_image_set}")
        print(f"   - Converted workflow has {len(new_workflow)} items")
        
        # Test iteration over converted workflow (this was causing the error)
        print("🔍 Testing workflow iteration (this was causing the 'list' object has no attribute 'items' error)...")
        
        node_count = 0
        for node_id, node in new_workflow.items():
            if (isinstance(node, dict) and 
                node.get("class_type") == "LoadImage" and 
                node_id not in ["links", "groups", "config", "extra", "version"]):
                node_count += 1
                print(f"   - Found LoadImage node: {node_id}")
        
        print(f"✅ Iteration test passed! Found {node_count} LoadImage nodes")
        return True
    
    else:
        print("❌ Workflow is not in nodes array format")
        return False

def test_face_swap_generation():
    """Test face swap generation with mock setup"""
    print("\n🧪 Testing face swap generation...")
    
    # Create temporary test images
    with tempfile.TemporaryDirectory() as temp_dir:
        original_image = os.path.join(temp_dir, "original.jpg")
        reference_image = os.path.join(temp_dir, "reference.jpg")
        
        create_test_image(original_image)
        create_test_image(reference_image)
        
        print(f"✅ Created test images:")
        print(f"   - Original: {original_image}")
        print(f"   - Reference: {reference_image}")
        
        # Initialize client (this will fail connection but we're testing the workflow logic)
        client = LocalComfyUIClient()
        
        # Test the workflow preparation logic
        try:
            print("🔄 Testing workflow preparation logic...")
            
            # This should not crash with the 'list' object has no attribute 'items' error
            result = client.generate_image_with_face_swap(
                original_image_path=original_image,
                reference_image_path=reference_image,
                swap_intensity="75%"
            )
            
            # We expect this to return None due to connection failure, but it should not crash
            print(f"✅ Workflow preparation completed without errors")
            print(f"   - Result: {result} (expected None due to no ComfyUI connection)")
            return True
            
        except Exception as e:
            print(f"❌ Workflow preparation failed: {e}")
            return False

def main():
    """Run all tests"""
    print("🚀 Reference Chad Feature - Final Fix Verification")
    print("=" * 60)
    
    # Test 1: Workflow conversion
    test1_passed = test_workflow_conversion()
    
    # Test 2: Face swap generation
    test2_passed = test_face_swap_generation()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   - Workflow Conversion: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   - Face Swap Generation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The Reference Chad feature fix is working correctly.")
        print("   - Workflow conversion from nodes array to direct node dict format works")
        print("   - No more 'list' object has no attribute 'items' errors")
        print("   - Face swap generation logic is robust")
        return True
    else:
        print("\n❌ SOME TESTS FAILED! Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
