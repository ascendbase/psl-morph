"""
Test basic ComfyUI functionality with minimal workflow
"""

import os
import requests
import base64
import json
from dotenv import load_dotenv

def test_basic_comfyui():
    """Test with the most basic ComfyUI workflow possible"""
    
    print("🧪 TESTING BASIC COMFYUI WORKFLOW")
    print("=" * 50)
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"Endpoint ID: {endpoint_id}")
    
    if not api_key or not endpoint_id:
        print("❌ Missing credentials!")
        return
    
    # Test image
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    # Convert image to base64
    with open(test_image, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"✅ Test image loaded: {test_image}")
    
    # Ultra-simple workflow - just text to image
    simple_workflow = {
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 10,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "a beautiful landscape",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "ugly, blurry, bad quality",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "test_output",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    # Prepare payload
    payload = {
        "input": {
            "workflow": simple_workflow
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🚀 Testing basic text-to-image workflow...")
    
    try:
        response = requests.post(
            f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Basic workflow succeeded!")
            print(f"Response keys: {list(result.keys())}")
            
            if 'output' in result:
                output = result['output']
                print(f"Output keys: {list(output.keys()) if output else 'None'}")
                return True
            else:
                print(f"⚠️ No output in response")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_flux_workflow():
    """Test with FLUX workflow since the image name suggests FLUX"""
    
    print(f"\n🧪 TESTING FLUX WORKFLOW")
    print("=" * 30)
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    # FLUX workflow
    flux_workflow = {
        "6": {
            "inputs": {
                "text": "a beautiful landscape, high quality",
                "clip": ["11", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 0]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "flux_test",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        },
        "10": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "11": {
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        },
        "12": {
            "inputs": {
                "unet_name": "flux1-schnell.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader"
        },
        "13": {
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["27", 0]
            },
            "class_type": "SamplerCustomAdvanced"
        },
        "16": {
            "inputs": {
                "sampler_name": "euler"
            },
            "class_type": "KSamplerSelect"
        },
        "17": {
            "inputs": {
                "scheduler": "simple",
                "steps": 4,
                "denoise": 1.0,
                "model": ["12", 0]
            },
            "class_type": "BasicScheduler"
        },
        "22": {
            "inputs": {
                "model": ["12", 0],
                "conditioning": ["6", 0]
            },
            "class_type": "BasicGuider"
        },
        "25": {
            "inputs": {
                "noise_seed": 42
            },
            "class_type": "RandomNoise"
        },
        "27": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        }
    }
    
    payload = {
        "input": {
            "workflow": flux_workflow
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FLUX workflow succeeded!")
            print(f"Response keys: {list(result.keys())}")
            return True
        else:
            print(f"❌ FLUX workflow failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FLUX Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing different workflow types to find what works...\n")
    
    # Test basic workflow first
    basic_success = test_basic_comfyui()
    
    if not basic_success:
        # Try FLUX workflow since the Docker image mentions "flux1-schnell"
        flux_success = test_flux_workflow()
        
        if flux_success:
            print(f"\n🎉 SUCCESS! FLUX workflow works!")
            print(f"Your endpoint is running FLUX models.")
        else:
            print(f"\n❌ Both workflows failed.")
            print(f"The endpoint might need a different Docker image.")
    else:
        print(f"\n🎉 SUCCESS! Basic workflow works!")
