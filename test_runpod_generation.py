import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# RunPod endpoint URL
RUNPOD_ENDPOINT = os.getenv('RUNPOD_ENDPOINT_URL', 'https://api.runpod.ai/v2/psl-morph/runsync')
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY')

def test_runpod_generation():
    """Test if RunPod endpoint can generate images"""
    
    print("🔍 Testing RunPod Generation...")
    print(f"Endpoint: {RUNPOD_ENDPOINT}")
    
    # Simple test workflow
    test_workflow = {
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "KSampler"}
        },
        "4": {
            "inputs": {
                "ckpt_name": "real-dream-15.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "Load Checkpoint"}
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Empty Latent Image"}
        },
        "6": {
            "inputs": {
                "text": "beautiful woman, portrait, high quality"
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Prompt)"}
        },
        "7": {
            "inputs": {
                "text": "bad quality, blurry"
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Negative)"}
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "9": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"}
        }
    }
    
    # Connect CLIP to checkpoint
    test_workflow["6"]["inputs"]["clip"] = ["4", 1]
    test_workflow["7"]["inputs"]["clip"] = ["4", 1]
    
    payload = {
        "input": {
            "workflow": test_workflow
        }
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📤 Sending test workflow...")
        response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers, timeout=120)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Generation successful!")
            print(f"Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing generation: {e}")
        return False

def test_impact_pack_nodes():
    """Test if Impact Pack nodes are available"""
    
    print("\n🔍 Testing Impact Pack Nodes...")
    
    # Test workflow with Impact Pack nodes
    impact_workflow = {
        "1": {
            "inputs": {
                "ckpt_name": "real-dream-15.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "bbox_detector": "face_yolov8m.pt",
                "bbox_threshold": 0.5,
                "bbox_dilation": 10,
                "crop_factor": 3.0,
                "drop_size": 10,
                "sub_threshold": 0.5,
                "sub_dilation": 0,
                "sub_bbox_expansion": 0,
                "sam_model_opt": "sam_vit_b_01ec64.pth",
                "segm_detector_opt": "bbox/face_yolov8m.pt",
                "sam_threshold": 0.93,
                "sam_bbox_expansion": 0,
                "sam_mask_hint_threshold": 0.7,
                "sam_mask_hint_use_negative": "False",
                "drop_size2": 10,
                "wildcard": "",
                "cycle": 1,
                "inpaint_model": False,
                "noise_mask": True,
                "force_inpaint": True,
                "bbox_expansion": 0,
                "order_of_processing": "left-to-right",
                "save_cropped_image": ["Save to temp", "Always save to temp (slow)"]
            },
            "class_type": "UltralyticsDetectorProvider"
        }
    }
    
    payload = {
        "input": {
            "workflow": impact_workflow
        }
    }
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📤 Testing Impact Pack nodes...")
        response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Impact Pack nodes available!")
            return True
        else:
            print(f"❌ Impact Pack test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Impact Pack: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RunPod Generation Test")
    print("=" * 50)
    
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY not found in .env file")
        exit(1)
    
    # Test basic generation
    basic_test = test_runpod_generation()
    
    # Test Impact Pack
    impact_test = test_impact_pack_nodes()
    
    print("\n📊 Test Results:")
    print(f"Basic Generation: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Impact Pack: {'✅ PASS' if impact_test else '❌ FAIL'}")
    
    if not basic_test:
        print("\n🔧 Troubleshooting:")
        print("1. Check if RunPod endpoint is deployed and running")
        print("2. Verify API key is correct")
        print("3. Check if models are loaded properly")
        print("4. Review RunPod logs for errors")
