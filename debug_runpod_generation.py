"""
Debug RunPod Generation - Find out why generation isn't working
"""

import os
import sys
import json
import time
import logging
from dotenv import load_dotenv
from runpod_client import RunPodClient

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_runpod_generation():
    """Test RunPod generation step by step"""
    
    print("🔍 DEBUGGING RUNPOD GENERATION")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    API_KEY = os.getenv('RUNPOD_API_KEY')
    ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID')
    
    print(f"API Key: {'✅ Found' if API_KEY else '❌ Missing'}")
    print(f"Endpoint ID: {ENDPOINT_ID if ENDPOINT_ID else '❌ Missing'}")
    
    if not API_KEY or not ENDPOINT_ID:
        print("\n❌ Missing RunPod credentials!")
        print("Please set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID in .env file")
        return
    
    # Initialize client
    print(f"\n🔌 Initializing RunPod client...")
    try:
        client = RunPodClient(API_KEY, ENDPOINT_ID)
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return
    
    # Test connection
    print(f"\n🌐 Testing connection...")
    try:
        connected = client.test_connection()
        print(f"Connection: {'✅ Success' if connected else '❌ Failed'}")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return
    
    # Check if we have a test image
    test_image_path = None
    possible_paths = [
        "uploads/test_image.jpg",
        "uploads/test_image.png", 
        "test_image.jpg",
        "test_image.png"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print(f"\n📸 Creating test image...")
        # Create a simple test image
        from PIL import Image
        import numpy as np
        
        # Create a 512x512 test image
        test_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        test_img = Image.fromarray(test_array)
        test_image_path = "test_image.png"
        test_img.save(test_image_path)
        print(f"✅ Created test image: {test_image_path}")
    else:
        print(f"✅ Found test image: {test_image_path}")
    
    # Test generation
    print(f"\n🎨 Testing generation...")
    print(f"Image: {test_image_path}")
    print(f"Preset: HTN")
    print(f"Denoise Intensity: 5")
    
    try:
        result, error = client.generate_image(test_image_path, 'HTN', 5)
        
        if error:
            print(f"❌ Generation failed: {error}")
            return
        
        print(f"✅ Generation started!")
        print(f"Result type: {type(result)}")
        print(f"Result: {str(result)[:100]}...")
        
        # If it's a job ID, wait for completion
        if isinstance(result, str) and not result.startswith('data:'):
            print(f"\n⏳ Waiting for job completion...")
            job_id = result
            
            start_time = time.time()
            timeout = 120  # 2 minutes
            
            while time.time() - start_time < timeout:
                status, output = client.check_status(job_id)
                print(f"Status: {status}")
                
                if status == 'COMPLETED':
                    print(f"✅ Generation completed!")
                    print(f"Output type: {type(output)}")
                    
                    if output:
                        # Save result
                        result_path = f"debug_result_{int(time.time())}.png"
                        success = client.save_result_image(output, result_path)
                        if success:
                            print(f"✅ Result saved to: {result_path}")
                        else:
                            print(f"❌ Failed to save result")
                    else:
                        print(f"❌ No output received")
                    return
                
                elif status == 'FAILED':
                    print(f"❌ Generation failed: {output}")
                    return
                
                time.sleep(5)
            
            print(f"❌ Generation timed out after {timeout} seconds")
        
        # If it's direct base64 result
        elif isinstance(result, str) and result.startswith('data:'):
            print(f"✅ Got direct result!")
            result_path = f"debug_result_{int(time.time())}.png"
            success = client.save_result_image(result, result_path)
            if success:
                print(f"✅ Result saved to: {result_path}")
            else:
                print(f"❌ Failed to save result")
        
        else:
            print(f"❌ Unexpected result format: {type(result)}")
            print(f"Result: {result}")
    
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()

def test_workflow_creation():
    """Test workflow creation"""
    print(f"\n🔧 Testing workflow creation...")
    
    try:
        from runpod_client import RunPodClient
        
        # Create a dummy client to test workflow creation
        client = RunPodClient("dummy", "dummy")
        
        # Test workflow creation
        workflow = client.create_simple_workflow("test.jpg", "HTN", 5)
        
        print(f"✅ Workflow created successfully")
        print(f"Workflow nodes: {list(workflow.keys())}")
        
        # Check key nodes
        required_nodes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for node in required_nodes:
            if node in workflow:
                print(f"  ✅ Node {node}: {workflow[node]['class_type']}")
            else:
                print(f"  ❌ Node {node}: Missing")
        
        # Check settings
        settings = client.get_morph_settings("HTN", 5)
        print(f"✅ Settings: {settings}")
        
    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_creation()
    test_runpod_generation()
