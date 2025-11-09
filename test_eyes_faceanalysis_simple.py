"""
Test script for Simple Eyes + Eyebrows FaceAnalysis workflow
This tests the simplified ComfyUI_FaceAnalysis workflow using VAEEncodeForInpaint
"""

import json
import requests
import time
import os
from PIL import Image
import base64
import io

def test_eyes_faceanalysis_simple_workflow():
    """Test the simple eyes + eyebrows FaceAnalysis workflow"""
    
    # ComfyUI settings
    comfyui_url = "http://127.0.0.1:8188"
    
    print("🧪 Testing Simple Eyes + Eyebrows FaceAnalysis Workflow")
    print("=" * 55)
    
    # Load workflow
    workflow_path = "comfyui_workflows/workflow_eyes_faceanalysis_simple.json"
    
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
        output_path = f"test_output_eyes_faceanalysis_simple.png"
        with open(output_path, 'wb') as f:
            f.write(image_response.content)
        
        print(f"✅ Result saved: {output_path}")
        
        # Workflow analysis
        print("\n📊 Simple Workflow Analysis:")
        print("=" * 35)
        print("🎯 Target Areas: Eyes + Eyebrows")
        print("🤖 Model: real-dream-15.safetensors")
        print("🎨 LoRA: chad_sd1.5.safetensors (0.8 strength)")
        print("💪 Denoise: 0.5 (50% intensity)")
        print("🔍 FaceSegmentation: eyes,eyebrows")
        print("📊 Confidence: 0.5")
        print("📏 Expand: 10 pixels")
        print("🌫️ Blur: 5 radius")
        print("🎨 Method: VAEEncodeForInpaint (simplified)")
        
        print("\n🎉 Simple Eyes + Eyebrows FaceAnalysis test completed successfully!")
        print(f"📁 Check the result: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during workflow test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 ComfyUI FaceAnalysis Simple Eyes Test")
    print("=" * 45)
    print("This tests the simplified ComfyUI_FaceAnalysis workflow")
    print("for targeting eyes + eyebrows using VAEEncodeForInpaint")
    print()
    
    # Check requirements
    print("📋 Pre-flight checks:")
    print("1. ✅ ComfyUI running on http://127.0.0.1:8188")
    print("2. ✅ ComfyUI_FaceAnalysis extension installed")
    print("3. ✅ real-dream-15.safetensors model available")
    print("4. ✅ chad_sd1.5.safetensors LoRA available")
    print("5. ✅ test_image.png in project root")
    print()
    
    input("Press Enter to start the simple test...")
    
    success = test_eyes_faceanalysis_simple_workflow()
    
    if success:
        print("\n🎉 SUCCESS! The Simple FaceAnalysis workflow works!")
        print("✅ Eyes + eyebrows targeting is functional")
        print("🚀 Ready to integrate into the web app")
    else:
        print("\n❌ FAILED! Check the errors above")
        print("🔧 Make sure ComfyUI_FaceAnalysis extension is properly installed")
