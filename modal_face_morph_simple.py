"""
Simplified Modal.com implementation for face morphing
Basic ComfyUI with SD 1.5 and LoRA support - no custom nodes
"""

import modal
import os
import json
import base64
import io
from PIL import Image
import requests
import time

# Create Modal app
app = modal.App("face-morph-simple")

# Create persistent volume for models
models_volume = modal.Volume.from_name("face-models", create_if_missing=True)

# Define the simplified ComfyUI image
comfyui_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "wget", "curl", "unzip")
    .pip_install([
        "torch==2.0.1",
        "torchvision==0.15.2", 
        "torchaudio==2.0.2",
        "xformers==0.0.20",
        "transformers==4.30.2",
        "diffusers==0.18.2",
        "accelerate==0.20.3",
        "safetensors==0.3.1",
        "opencv-python==4.8.0.74",
        "pillow==10.0.0",
        "numpy==1.24.3",
        "requests==2.31.0",
        "aiohttp==3.8.4",
        "websockets==11.0.3",
        "psutil==5.9.5"
    ])
    .run_commands([
        # Clone ComfyUI (basic installation only)
        "cd /root && git clone https://github.com/comfyanonymous/ComfyUI.git",
        
        # Create necessary directories
        "mkdir -p /root/ComfyUI/models/checkpoints",
        "mkdir -p /root/ComfyUI/models/loras",
        "mkdir -p /root/ComfyUI/models/vae",
        "mkdir -p /root/ComfyUI/models/embeddings",
        "mkdir -p /root/ComfyUI/input",
        "mkdir -p /root/ComfyUI/output",
        
        # Download essential models
        "cd /root/ComfyUI/models/checkpoints && wget -O realdream_v12.safetensors https://huggingface.co/SG161222/RealVisXL_V4.0/resolve/main/RealVisXL_V4.0.safetensors"
    ])
)

@app.function(
    image=comfyui_image,
    volumes={"/models": models_volume},
    gpu="T4",  # T4 for cost efficiency
    timeout=600,  # 10 minutes max
    memory=16384,  # 16GB RAM
    cpu=4
)
def generate_face_morph(image_b64: str, preset_key: str, denoise_strength: float = 0.15):
    """
    Generate face morph using basic ComfyUI with SD 1.5 and LoRA
    
    Args:
        image_b64: Base64 encoded input image
        preset_key: Preset key (tier1, tier2, chad)
        denoise_strength: Denoise strength (0.10-0.25)
    
    Returns:
        tuple: (result_image_b64, error_message)
    """
    import subprocess
    import uuid
    
    try:
        print(f"🚀 Starting face morph generation with preset: {preset_key}")
        
        # Decode input image
        image_data = base64.b64decode(image_b64)
        input_image = Image.open(io.BytesIO(image_data))
        
        # Save input image
        input_filename = f"input_{uuid.uuid4().hex}.png"
        input_path = f"/root/ComfyUI/input/{input_filename}"
        input_image.save(input_path)
        
        print(f"✅ Input image saved: {input_path}")
        
        # Copy models from persistent volume to ComfyUI
        print("📁 Copying models from persistent storage...")
        os.system("cp -r /models/lora/* /root/ComfyUI/models/loras/ 2>/dev/null || true")
        os.system("cp -r /models/base_models/* /root/ComfyUI/models/checkpoints/ 2>/dev/null || true")
        
        # Start ComfyUI server
        print("🔧 Starting ComfyUI server...")
        comfyui_process = subprocess.Popen([
            "python", "/root/ComfyUI/main.py", 
            "--listen", "127.0.0.1", 
            "--port", "8188",
            "--disable-auto-launch"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        max_wait = 120  # 120 seconds max wait
        wait_time = 0
        server_ready = False
        
        while wait_time < max_wait:
            try:
                response = requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
                if response.status_code == 200:
                    server_ready = True
                    break
            except requests.exceptions.RequestException as e:
                print(f"⏳ Waiting for ComfyUI server... ({wait_time}s) - {e}")

            time.sleep(5)
            wait_time += 5
        
        if not server_ready:
            stdout, stderr = comfyui_process.communicate()
            print(f"❌ ComfyUI server failed to start. STDOUT: {stdout.decode()}, STDERR: {stderr.decode()}")
            return None, "ComfyUI server failed to start"
        
        print("✅ ComfyUI server ready!")
        
        # Create basic img2img workflow
        workflow = create_basic_workflow(input_filename, preset_key, denoise_strength)
        
        # Queue workflow
        print("🎯 Queuing workflow...")
        prompt_id = str(uuid.uuid4())
        payload = {
            "prompt": workflow,
            "client_id": prompt_id
        }
        
        response = requests.post("http://127.0.0.1:8188/prompt", json=payload, timeout=30)
        if response.status_code != 200:
            return None, f"Failed to queue workflow: {response.text}"
        
        result = response.json()
        actual_prompt_id = result.get('prompt_id', prompt_id)
        
        print(f"✅ Workflow queued with ID: {actual_prompt_id}")
        
        # Wait for completion
        max_generation_time = 300  # 5 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_generation_time:
            try:
                response = requests.get(f"http://127.0.0.1:8188/history/{actual_prompt_id}", timeout=10)
                if response.status_code == 200:
                    history = response.json()
                    if actual_prompt_id in history:
                        print("✅ Generation completed!")
                        
                        # Get output image
                        result_image = get_output_image(history[actual_prompt_id])
                        if result_image:
                            # Convert to base64
                            buffered = io.BytesIO()
                            result_image.save(buffered, format="PNG")
                            result_b64 = base64.b64encode(buffered.getvalue()).decode()
                            
                            print("🎉 Face morph generation successful!")
                            return result_b64, None
                        else:
                            return None, "Failed to retrieve output image"
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
            
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            print(f"⏳ Generation in progress... ({elapsed}s)")
        
        return None, "Generation timed out"
        
    except Exception as e:
        print(f"❌ Error in face morph generation: {e}")
        return None, str(e)
    
    finally:
        # Cleanup
        try:
            comfyui_process.terminate()
            comfyui_process.wait(timeout=10)
        except:
            try:
                comfyui_process.kill()
            except:
                pass

def create_basic_workflow(input_filename: str, preset_key: str, denoise_strength: float):
    """Create a basic img2img workflow with LoRA support"""
    import random
    
    # Select LoRA based on preset
    lora_map = {
        "tier1": "chad_sd1.5.safetensors",
        "tier2": "chad_sd1.5.safetensors", 
        "chad": "chad_sd1.5.safetensors"
    }
    
    lora_name = lora_map.get(preset_key, "face_morph.safetensors")
    
    # Generate unique seed
    unique_seed = random.randint(1, 2**32 - 1)
    
    return {
        "1": {
            "inputs": {
                "ckpt_name": "realdream_v12.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "lora_name": lora_name,
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["1", 0],
                "clip": ["1", 1]
            },
            "class_type": "LoraLoader"
        },
        "3": {
            "inputs": {
                "text": f"face morph, {preset_key}, high quality, detailed, realistic",
                "clip": ["2", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "4": {
            "inputs": {
                "text": "blurry, low quality, distorted, deformed, ugly",
                "clip": ["2", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {
                "image": input_filename
            },
            "class_type": "LoadImage"
        },
        "7": {
            "inputs": {
                "seed": unique_seed,
                "steps": 25,
                "cfg": 8.0,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": denoise_strength,
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "9": {
            "inputs": {
                "filename_prefix": f"morph_{preset_key}_{int(time.time())}",
                "images": ["7", 0]
            },
            "class_type": "SaveImage"
        }
    }

def get_output_image(history_data: dict):
    """Extract output image from ComfyUI history"""
    try:
        outputs = history_data.get('outputs', {})
        
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for image_info in node_output['images']:
                    filename = image_info['filename']
                    subfolder = image_info.get('subfolder', '')
                    
                    # Download the image
                    params = {
                        'filename': filename,
                        'subfolder': subfolder,
                        'type': 'output'
                    }
                    
                    response = requests.get("http://127.0.0.1:8188/view", params=params, timeout=30)
                    if response.status_code == 200:
                        return Image.open(io.BytesIO(response.content))
        
        return None
    except Exception as e:
        print(f"Error getting output image: {e}")
        return None

# Test function
@app.function(
    image=comfyui_image,
    volumes={"/models": models_volume},
    gpu="T4"
)
def test_setup():
    """Test the simplified Modal setup"""
    print("🧪 Testing simplified Modal setup...")
    
    # Check ComfyUI installation
    if os.path.exists("/root/ComfyUI/main.py"):
        print("✅ ComfyUI installed")
    else:
        print("❌ ComfyUI not found")
    
    # Check models
    checkpoints = os.listdir("/root/ComfyUI/models/checkpoints")
    print(f"📁 Available checkpoints: {checkpoints}")
    
    # Check for LoRAs in persistent storage
    if os.path.exists("/models"):
        print("✅ Models volume mounted")
        if os.path.exists("/models/lora"):
            loras = os.listdir("/models/lora")
            print(f"📁 Available LoRAs: {loras}")
        else:
            print("⚠️ No LoRAs found in persistent storage")
    else:
        print("❌ Models volume not mounted")
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU available: {gpu_name}")
        else:
            print("❌ No GPU available")
    except:
        print("❌ PyTorch not available")
    
    return "Simplified setup test completed"

# Local development function
@app.local_entrypoint()
def main():
    """Local entrypoint for testing"""
    print("🚀 Testing simplified Modal face morph setup...")
    result = test_setup.remote()
    print(f"Test result: {result}")

if __name__ == "__main__":
    main()
