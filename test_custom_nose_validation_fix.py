#!/usr/bin/env python3
"""
Test script to verify custom nose feature works with correct area validation
"""

import json
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_workflow_validation():
    """Test that all custom feature workflows use valid area names"""
    
    # Valid areas according to ComfyUI FaceSegmentation
    valid_areas = ['face', 'main_features', 'eyes', 'left_eye', 'right_eye', 'nose', 'mouth', 'face+forehead (if available)']
    
    # Test workflows
    workflows_to_test = {
        'nose': 'comfyui_workflows/workflow_custom_nose.json',
        'eyes': 'comfyui_workflows/workflow_custom_eyes.json', 
        'mouth': 'comfyui_workflows/workflow_custom_mouth.json'
    }
    
    all_valid = True
    
    for feature, workflow_path in workflows_to_test.items():
        logger.info(f"Testing {feature} workflow: {workflow_path}")
        
        if not os.path.exists(workflow_path):
            logger.error(f"Workflow file not found: {workflow_path}")
            all_valid = False
            continue
            
        try:
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Find FaceSegmentation node (usually node 6)
            face_seg_node = None
            for node_id, node_data in workflow.items():
                if node_data.get('class_type') == 'FaceSegmentation':
                    face_seg_node = node_data
                    break
            
            if not face_seg_node:
                logger.error(f"No FaceSegmentation node found in {workflow_path}")
                all_valid = False
                continue
            
            area = face_seg_node['inputs'].get('area')
            if area not in valid_areas:
                logger.error(f"Invalid area '{area}' in {workflow_path}. Valid areas: {valid_areas}")
                all_valid = False
            else:
                logger.info(f"✓ {feature} workflow uses valid area: '{area}'")
                
        except Exception as e:
            logger.error(f"Error reading {workflow_path}: {e}")
            all_valid = False
    
    return all_valid

def test_client_mapping():
    """Test that local_comfyui_client.py has correct feature mappings"""
    
    try:
        # Import the client to check supported features
        sys.path.append('.')
        from local_comfyui_client import LocalComfyUIClient
        
        # Create client instance (without connecting)
        client = LocalComfyUIClient(base_url="http://dummy")
        
        logger.info("Testing client feature mappings:")
        
        expected_features = ['eyes', 'nose', 'mouth']
        actual_features = list(client.supported_features.keys())
        
        # Check that chin is removed
        if 'chin' in actual_features:
            logger.error("❌ 'chin' feature should be removed from supported_features")
            return False
        else:
            logger.info("✓ 'chin' feature correctly removed")
        
        # Check expected features are present
        for feature in expected_features:
            if feature not in actual_features:
                logger.error(f"❌ Missing expected feature: {feature}")
                return False
            else:
                area = client.supported_features[feature]['area']
                logger.info(f"✓ {feature} -> area: '{area}'")
        
        # Check mouth uses 'mouth' not 'lips'
        mouth_area = client.supported_features['mouth']['area']
        if mouth_area != 'mouth':
            logger.error(f"❌ Mouth feature should use area 'mouth', not '{mouth_area}'")
            return False
        else:
            logger.info("✓ Mouth feature correctly uses area 'mouth'")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing client mapping: {e}")
        return False

def main():
    """Run all validation tests"""
    
    logger.info("=== Custom Nose Feature Validation Fix Test ===")
    
    # Test 1: Workflow validation
    logger.info("\n1. Testing workflow area validation...")
    workflow_valid = test_workflow_validation()
    
    # Test 2: Client mapping
    logger.info("\n2. Testing client feature mapping...")
    client_valid = test_client_mapping()
    
    # Summary
    logger.info("\n=== Test Results ===")
    if workflow_valid and client_valid:
        logger.info("✅ All tests passed! Custom features should work correctly.")
        logger.info("✅ Validation errors should be fixed.")
        logger.info("✅ Available features: Eyes, Nose, Mouth")
        return True
    else:
        logger.error("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
