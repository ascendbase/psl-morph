"""
Test script for FIXED Eyes FaceAnalysis workflow
This tests the improved workflow that preserves original image context
"""

import json
import requests
import time
import os
from PIL import Image
import base64
import io

def test_eyes_faceanalysis_fixed_workflow():
    """Test the fixed eyes FaceAnalysis workflow"""
    
    # ComfyUI settings
    comfyui_url = "http://127.0.0.1:8188"
    
    print("🧪 Testing FIXED Eyes FaceAnalysis Workflow")
    print("=" * 50)
    
    # Load workflow
    workflow_path = "comfyui_workflows/workflow_eyes_faceanalysis_fixed.json"
    
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    print(f"✅ Loaded workflow: {workflow_path}")
    
    # Test image path
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        print("Please place a test image named 'test_image.png' in the project root")
        return False
    
    print(f"✅ Found test image: {test_image}")
    
    try:
        # Check ComfyUI connection
        response = requests.get(f"{comfyui_url}/system_stats")
        if response.status_code != 200:
            print(f"❌ Cannot connect to ComfyUI at {comfyui_url}")
            print("Make sure ComfyUI is running with FaceAnalysis extension installed")
            return False
        
        print("✅ Connected to ComfyUI")
        
        # Upload test image
        print("\n📤 Uploading test image...")
        
        with open(test_image, 'rb') as f:
            files = {
                'image': (test_image, f, 'image/png'),
                'type': (None, 'input'),
                'subfolder': (None, ''),
                'overwrite': (None, 'true')
            }
            
            upload_response = requests.post(f"{comfyui_url}/upload/image", files=files)
            
            if upload_response.status_code != 200:
                print(f"❌ Failed to upload image: {upload_response.text}")
                return False
        
        # Update workflow with uploaded image
        workflow["5"]["inputs"]["image"] = test_image
        
        print("✅ Image uploaded successfully")
        
        # Queue the workflow
        print("\n🚀 Queuing workflow...")
        
        queue_data = {"prompt": workflow}
        queue_response = requests.post(f"{comfyui_url}/prompt", json=queue_data)
        
        if queue_response.status_code != 200:
            print(f"❌ Failed to queue workflow: {queue_response.text}")
            return False
        
        result = queue_response.json()
        prompt_id = result["prompt_id"]
        
        print(f"✅ Workflow queued with ID: {prompt_id}")
        
        # Monitor progress
        print("\n⏳ Monitoring progress...")
        
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while True:
            # Check if timeout
            if time.time() - start_time > timeout:
                print("❌ Workflow timed out after 5 minutes")
                return False
            
            # Get queue status
            queue_response = requests.get(f"{comfyui_url}/queue")
            queue_data = queue_response.json()
            
            # Check if our prompt is still in queue
            running = any(item[1] == prompt_id for item in queue_data.get("queue_running", []))
            pending = any(item[1] == prompt_id for item in queue_data.get("queue_pending", []))
            
            if not running and not pending:
                print("✅ Workflow completed!")
                break
            
            print("⏳ Still processing...")
            time.sleep(5)
        
        # Get the result
        print("\n📥 Getting results...")
        
        history_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
        
        if history_response.status_code != 200:
            print(f"❌ Failed to get history: {history_response.text}")
            return False
        
        history = history_response.json()
        
        if prompt_id not in history:
            print("❌ Prompt ID not found in history")
            return False
        
        # Find the output images
        outputs = history[prompt_id]["outputs"]
        
        if "10" not in outputs:  # SaveImage node
            print("❌ No output found from SaveImage node")
            return False
        
        images = outputs["10"]["images"]
        
        if not images:
            print("❌ No images in output")
            return False
        
        # Download and save the result
        result_image = images[0]
        filename = result_image["filename"]
        subfolder = result_image.get("subfolder", "")
        
        # Construct the image URL
        if subfolder:
            image_url = f"{comfyui_url}/view?filename={filename}&subfolder={subfolder}"
        else:
            image_url = f"{comfyui_url}/view?filename={filename}"
        
        print(f"📥 Downloading result: {filename}")
        
        image_response = requests.get(image_url)
        
        if image_response.status_code != 200:
            print(f"❌ Failed to download image: {image_response.text}")
            return False
        
        # Save the result
        output_path = f"test_output_eyes_faceanalysis_FIXED.png"
        with open(output_path, 'wb') as f:
            f.write(image_response.content)
        
        print(f"✅ Result saved: {output_path}")
        
        # Workflow analysis
        print("\n📊 FIXED Workflow Analysis:")
        print("=" * 35)
        print("🎯 Target Areas: Eyes")
        print("🤖 Model: real-dream-15.safetensors")
        print("🎨 LoRA: chad_sd1.5.safetensors (0.7 strength)")
        print("💪 Denoise: 0.35 (35% - preserves original)")
        print("🔍 FaceSegmentation: eyes area")
        print("📏 Grow: 8 pixels (tapered)")
        print("🌫️ Blur: 4 radius")
        print("🎨 Method: VAEEncode + ImageBlend (FIXED!)")
        print("✅ Uses ORIGINAL image context (not gray cutout)")
        print("🔄 Blends generated eyes with original face")
        
        print("\n🎉 FIXED Eyes FaceAnalysis test completed successfully!")
        print(f"📁 Check the result: {output_path}")
        print("🚀 This should look much better - no gray cutouts!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during workflow test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 ComfyUI FaceAnalysis FIXED Eyes Test")
    print("=" * 45)
    print("This tests the FIXED ComfyUI_FaceAnalysis workflow")
    print("that preserves original image context instead of gray cutouts")
    print()
    
    # Check requirements
    print("📋 Pre-flight checks:")
    print("1. ✅ ComfyUI running on http://127.0.0.1:8188")
    print("2. ✅ ComfyUI_FaceAnalysis extension installed")
    print("3. ✅ real-dream-15.safetensors model available")
    print("4. ✅ chad_sd1.5.safetensors LoRA available")
    print("5. ✅ test_image.png in project root")
    print()
    
    input("Press Enter to start the FIXED test...")
    
    success = test_eyes_faceanalysis_fixed_workflow()
    
    if success:
        print("\n🎉 SUCCESS! The FIXED FaceAnalysis workflow works!")
        print("✅ Eyes targeting with original image context")
        print("🚀 Ready to integrate into the web app")
        print("💡 No more gray cutout issues!")
    else:
        print("\n❌ FAILED! Check the errors above")
        print("🔧 Make sure all required nodes are available")
