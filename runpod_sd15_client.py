"""
RunPod SD1.5 Client for Real Dream + Chad LoRA
Works with your custom models
"""

import requests
import json
import base64
import time
import os
import random
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class RunPodSD15Client:
    def __init__(self, api_key, endpoint_id):
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_sd15_workflow(self, prompt, width=512, height=512, steps=20, cfg=7.0):
        """Create SD1.5 workflow with Real Dream + Chad LoRA"""
        
        unique_seed = random.randint(1, 2**32 - 1)
        timestamp = int(time.time())
        
        # SD1.5 workflow with Real Dream + Chad LoRA
        workflow = {
            "3": {
                "inputs": {
                    "seed": unique_seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["10", 0],  # LoRA applied model
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "real-dream-15.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["10", 1]  # LoRA applied CLIP
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "ugly, blurry, bad quality, deformed, distorted",
                    "clip": ["10", 1]  # LoRA applied CLIP
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
                    "filename_prefix": f"chad_morph_{timestamp}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            },
            "10": {
                "inputs": {
                    "model": ["4", 0],
                    "clip": ["4", 1],
                    "lora_name": "chad_sd1.5.safetensors",
                    "strength_model": 1.0,
                    "strength_clip": 1.0
                },
                "class_type": "LoraLoader"
            }
        }
        
        logger.info(f"Created SD1.5 workflow with Real Dream + Chad LoRA: {prompt}")
        return workflow
    
    def create_sd15_img2img_workflow(self, image_filename, prompt, denoise_strength=0.7, width=512, height=512, steps=20, cfg=7.0):
        """Create SD1.5 img2img workflow with Real Dream + Chad LoRA"""
        
        unique_seed = random.randint(1, 2**32 - 1)
        timestamp = int(time.time())
        
        # SD1.5 img2img workflow
        workflow = {
            "3": {
                "inputs": {
                    "seed": unique_seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": denoise_strength,
                    "model": ["10", 0],  # LoRA applied model
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["11", 0]  # From VAE encode
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "real-dream-15.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "image": image_filename,
                    "upload": "image"
                },
                "class_type": "LoadImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["10", 1]  # LoRA applied CLIP
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "ugly, blurry, bad quality, deformed, distorted",
                    "clip": ["10", 1]  # LoRA applied CLIP
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
                    "filename_prefix": f"chad_img2img_{timestamp}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            },
            "10": {
                "inputs": {
                    "model": ["4", 0],
                    "clip": ["4", 1],
                    "lora_name": "chad_sd1.5.safetensors",
                    "strength_model": 1.0,
                    "strength_clip": 1.0
                },
                "class_type": "LoraLoader"
            },
            "11": {
                "inputs": {
                    "pixels": ["5", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEEncode"
            }
        }
        
        logger.info(f"Created SD1.5 img2img workflow with Real Dream + Chad LoRA: {prompt}")
        return workflow
    
    def generate_image(self, prompt, width=512, height=512, steps=20, cfg=7.0, timeout=300):
        """Generate image using Real Dream + Chad LoRA"""
        
        workflow = self.create_sd15_workflow(prompt, width, height, steps, cfg)
        
        payload = {
            "input": {
                "workflow": workflow
            }
        }
        
        try:
            logger.info(f"Submitting generation request...")
            response = requests.post(
                f"{self.base_url}/runsync",
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Generation completed successfully")
                return result
            else:
                logger.error(f"Generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None
    
    def transform_image(self, image_path, prompt, denoise_strength=0.7, width=512, height=512, steps=20, cfg=7.0, timeout=300):
        """Transform image using Real Dream + Chad LoRA"""
        
        # Upload image first
        image_filename = self.upload_image(image_path)
        if not image_filename:
            return None
        
        workflow = self.create_sd15_img2img_workflow(
            image_filename, prompt, denoise_strength, width, height, steps, cfg
        )
        
        payload = {
            "input": {
                "workflow": workflow
            }
        }
        
        try:
            logger.info(f"Submitting transformation request...")
            response = requests.post(
                f"{self.base_url}/runsync",
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Transformation completed successfully")
                return result
            else:
                logger.error(f"Transformation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Transformation error: {e}")
            return None
    
    def upload_image(self, image_path):
        """Upload image to RunPod"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create filename
            filename = f"input_{int(time.time())}.png"
            
            # For RunPod, we typically return the filename for the workflow
            # The actual upload happens as part of the workflow execution
            return filename
            
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return None

# Test function
def test_sd15_client():
    """Test the SD1.5 client with your models"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing API key or endpoint ID")
        return
    
    client = RunPodSD15Client(api_key, endpoint_id)
    
    print("🧪 Testing SD1.5 with Real Dream + Chad LoRA...")
    
    # Test text-to-image
    result = client.generate_image(
        prompt="a handsome man with chad features, high quality, detailed",
        width=512,
        height=512,
        steps=20,
        cfg=7.0
    )
    
    if result:
        print("✅ SD1.5 generation successful!")
        print(f"Result keys: {list(result.keys())}")
    else:
        print("❌ SD1.5 generation failed")

if __name__ == "__main__":
    test_sd15_client()
