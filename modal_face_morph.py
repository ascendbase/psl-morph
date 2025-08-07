"""
Modal.com implementation for face morphing with custom models
Perfect balance of speed, cost, and functionality
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
app = modal.App("face-morph-app")

# Create persistent volume for models
models_volume = modal.Volume.from_name("face-models", create_if_missing=True)

# Define the ComfyUI image with all dependencies
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
        # Clone ComfyUI
        "cd /root && git clone https://github.com/comfyanonymous/ComfyUI.git",
        
        # Install ComfyUI Manager
        "cd /root/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git",
        
        # Install essential custom nodes
        "cd /root/ComfyUI/custom_nodes && git clone https://github.com/Gourieff/comfyui-reactor-node.git",
        "cd /root/ComfyUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
        "cd /root/ComfyUI/custom_nodes && git clone https://github.com/WASasquatch/was-node-suite-comfyui.git",
        
        # Install dependencies for custom nodes
        "cd /root/ComfyUI/custom_nodes/comfyui-reactor-node && pip install -r requirements.txt",
        "cd /root/ComfyUI/custom_nodes/ComfyUI-Impact-Pack && pip install -r requirements.txt",
        
        # Create necessary directories
        "mkdir -p /root/ComfyUI/models/checkpoints",
        "mkdir -p /root/ComfyUI/models/loras",
        "mkdir -p /root/ComfyUI/models/vae",
        "mkdir -p /root/ComfyUI/models/controlnet",
        "mkdir -p /root/ComfyUI/models/embeddings",
        "mkdir -p /root/ComfyUI/input",
        "mkdir -p /root/ComfyUI/output",
        
        # Download essential models
        "cd /root/ComfyUI/models/checkpoints && wget -O sd_v15.safetensors https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
        "cd /root/ComfyUI/models/vae && wget -O vae-ft-mse-840000-ema-pruned.safetensors https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors"
    ])
)

@app.function(
    image=comfyui_image,
    volumes={"/models": models_volume},
    gpu="T4",  # T4 for cost efficiency, can upgrade to A10G for speed
    timeout=600,  # 10 minutes max
    memory=16384,  # 16GB RAM
    cpu=4
)
def generate_face_morph(image_b64: str, preset_key: str, denoise_strength: float = 0.15):
    """
    Generate face morph using ComfyUI with custom models
    
    Args:
        image_b64: Base64 encoded input image
        preset_key: Preset key (tier1, tier2, chad)
        denoise_strength: Denoise strength (0.10-0.25)
    
    Returns:
        tuple: (result_image_b64, error_message)
    """
    import subprocess
    import threading
    import queue
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
        os.system("cp -r /models/comfyui_workflows/* /root/ComfyUI/ 2>/dev/null || true")
        
        # Start ComfyUI server
        print("🔧 Starting ComfyUI server...")
        comfyui_process = subprocess.Popen([
            "python", "/root/ComfyUI/main.py", 
            "--listen", "127.0.0.1", 
            "--port", "8188",
            "--disable-auto-launch"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        max_wait = 60  # 60 seconds max wait
        wait_time = 0
        server_ready = False
        
        while wait_time < max_wait:
            try:
                response = requests.get("http://127.0.0.1:8188/system_stats", timeout=2)
                if response.status_code == 200:
                    server_ready = True
                    break
            except:
                pass
            time.sleep(2)
            wait_time += 2
            print(f"⏳ Waiting for ComfyUI server... ({wait_time}s)")
        
        if not server_ready:
            return None, "ComfyUI server failed to start"
        
        print("✅ ComfyUI server ready!")
        
        # Load workflow template
        workflow_file = "workflow_facedetailer.json"  # Use FaceDetailer workflow
        try:
            with open(f"/root/ComfyUI/{workflow_file}", 'r') as f:
                workflow = json.load(f)
        except:
            # Fallback to basic workflow
            workflow = create_basic_workflow(input_filename, preset_key, denoise_strength)
        
        # Update workflow parameters
        workflow = update_workflow_parameters(workflow, input_filename, preset_key, denoise_strength)
        
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
    """Create a basic img2img workflow if no custom workflow is found"""
    return {
        "1": {
            "inputs": {
                "ckpt_name": "sd_v15.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "lora_name": "face_morph.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["1", 0],
                "clip": ["1", 1]
            },
            "class_type": "LoraLoader"
        },
        "3": {
            "inputs": {
                "text": f"face morph, {preset_key}, high quality, detailed",
                "clip": ["2", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "4": {
            "inputs": {
                "text": "blurry, low quality, distorted",
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
        "6": {
            "inputs": {
                "vae": ["1", 2],
                "pixels": ["5", 0]
            },
            "class_type": "VAEEncode"
        },
        "7": {
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "dpmpp_2m",
                "scheduler": "normal",
                "denoise": denoise_strength,
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["6", 0]
            },
            "class_type": "KSampler"
        },
        "8": {
            "inputs": {
                "samples": ["7", 0],
                "vae": ["1", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": f"morph_{preset_key}",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

def update_workflow_parameters(workflow: dict, input_filename: str, preset_key: str, denoise_strength: float):
    """Update workflow with specific parameters"""
    import random
    
    # Generate unique seed
    unique_seed = random.randint(1, 2**32 - 1)
    
    # Update LoadImage node (usually node 5)
    for node_id, node in workflow.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = input_filename
        
        # Update KSampler nodes
        elif node.get("class_type") == "KSampler":
            node["inputs"]["denoise"] = denoise_strength
            node["inputs"]["seed"] = unique_seed
        
        # Update FaceDetailer nodes
        elif node.get("class_type") == "FaceDetailer":
            node["inputs"]["denoise"] = denoise_strength
            node["inputs"]["seed"] = unique_seed
        
        # Update SaveImage nodes
        elif node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = f"morph_{preset_key}_{int(time.time())}"
    
    return workflow

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

# Test function for development
@app.function(
    image=comfyui_image,
    volumes={"/models": models_volume},
    gpu="T4"
)
def test_setup():
    """Test the Modal setup"""
    print("🧪 Testing Modal setup...")
    
    # Check ComfyUI installation
    if os.path.exists("/root/ComfyUI/main.py"):
        print("✅ ComfyUI installed")
    else:
        print("❌ ComfyUI not found")
    
    # Check models directory
    if os.path.exists("/models"):
        print("✅ Models volume mounted")
        print(f"📁 Models directory contents: {os.listdir('/models')}")
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
    
    return "Setup test completed"

# Local development function
@app.local_entrypoint()
def main():
    """Local entrypoint for testing"""
    print("🚀 Testing Modal face morph setup...")
    result = test_setup.remote()
    print(f"Test result: {result}")

if __name__ == "__main__":
    main()
