"""
RunPod Serverless Client for Simple IMG2IMG with Real Dream + Chad LoRA
NO CUSTOM NODES - 100% STABLE
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

class RunPodClient:
    def __init__(self, api_key, endpoint_id):
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_morph_settings(self, preset_key, denoise_intensity):
        """Get morph settings based on preset and denoise intensity"""
        
        # Base settings for each preset
        preset_settings = {
            'HTN': {
                'lora_strength': 0.6,
                'prompt': "chad, handsome man, attractive, masculine features, high quality",
                'base_denoise': 0.4
            },
            'Chadlite': {
                'lora_strength': 0.8,
                'prompt': "chad, very handsome man, muscular, attractive, strong jawline, high quality, detailed",
                'base_denoise': 0.6
            },
            'Chad': {
                'lora_strength': 1.0,
                'prompt': "chad, extremely handsome alpha male, perfect masculine features, muscular, strong square jaw, intense eyes, high quality, ultra detailed",
                'base_denoise': 0.8
            }
        }
        
        # Adjust denoise based on intensity (1-10 scale)
        base_denoise = preset_settings[preset_key]['base_denoise']
        denoise_adjustment = (denoise_intensity - 5) * 0.1  # -0.4 to +0.5
        final_denoise = max(0.1, min(1.0, base_denoise + denoise_adjustment))
        
        return {
            'lora_strength': preset_settings[preset_key]['lora_strength'],
            'prompt': preset_settings[preset_key]['prompt'],
            'denoise': final_denoise
        }
    
    def create_simple_workflow(self, image_filename, preset_key, denoise_intensity):
        """Create simple img2img workflow with Real Dream + Chad LoRA"""
        
        settings = self.get_morph_settings(preset_key, denoise_intensity)
        unique_seed = random.randint(1, 2**32 - 1)
        timestamp = int(time.time())
        
        # Simple workflow - NO CUSTOM NODES
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "real-dream-15.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {
                    "title": "Load Checkpoint"
                }
            },
            "2": {
                "inputs": {
                    "lora_name": "chad_sd1.5.safetensors",
                    "strength_model": settings['lora_strength'],
                    "strength_clip": settings['lora_strength'],
                    "model": ["1", 0],
                    "clip": ["1", 1]
                },
                "class_type": "LoraLoader",
                "_meta": {
                    "title": "Load LoRA"
                }
            },
            "3": {
                "inputs": {
                    "text": settings['prompt'],
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Prompt)"
                }
            },
            "4": {
                "inputs": {
                    "text": "ugly, deformed, blurry, bad quality, distorted, bad anatomy",
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Negative)"
                }
            },
            "5": {
                "inputs": {
                    "image": image_filename,
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "6": {
                "inputs": {
                    "pixels": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEEncode",
                "_meta": {
                    "title": "VAE Encode"
                }
            },
            "7": {
                "inputs": {
                    "seed": unique_seed,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": settings['denoise'],
                    "model": ["2", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["6", 0]
                },
                "class_type": "KSampler",
                "_meta": {
                    "title": "KSampler"
                }
            },
            "8": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {
                    "title": "VAE Decode"
                }
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"morph_{preset_key}_{timestamp}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            }
        }
        
        logger.info(f"Created simple workflow for {preset_key} with denoise {settings['denoise']} and LoRA strength {settings['lora_strength']}")
        return workflow
    
    def image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None
    
    def generate_image(self, image_path, preset_key, denoise_intensity):
        """Generate face morphing using simple ComfyUI workflow"""
        try:
            # Get image filename
            image_filename = os.path.basename(image_path)
            
            # Create simple workflow
            workflow = self.create_simple_workflow(image_filename, preset_key, denoise_intensity)
            
            # Convert image to base64
            image_base64 = self.image_to_base64(image_path)
            if not image_base64:
                logger.error("Failed to convert image to base64")
                return None, "Failed to process image"
            
            # Prepare payload for serverless endpoint
            # Support both old and new endpoint formats
            payload = {
                "input": {
                    "workflow": workflow,
                    "images": [
                        {
                            "name": image_filename,
                            "image": image_base64
                        }
                    ]
                }
            }
            
            # Submit job to serverless endpoint
            logger.info(f"Submitting RunPod job for {preset_key} preset with denoise intensity {denoise_intensity}")
            response = requests.post(
                f"{self.base_url}/runsync",  # Use runsync for immediate response
                json=payload,
                headers=self.headers,
                timeout=120  # 2 minute timeout for sync request
            )
            
            if response.status_code != 200:
                logger.error(f"RunPod submission failed: {response.status_code} - {response.text}")
                return None, f"RunPod error: {response.status_code}"
            
            result = response.json()
            
            # Check if we got output directly (sync response)
            if 'output' in result and result['output']:
                output = result['output']
                if 'images' in output and output['images']:
                    # Return the first image
                    return output['images'][0], None
                else:
                    logger.error(f"No images in output: {output}")
                    return None, "No images generated"
            else:
                # If async, get job ID
                job_id = result.get('id')
                if job_id:
                    logger.info(f"RunPod job submitted: {job_id}")
                    return job_id, None
                else:
                    logger.error(f"No job ID or output returned: {result}")
                    return None, "No job ID returned from RunPod"
            
        except Exception as e:
            logger.error(f"RunPod submission error: {e}")
            return None, str(e)
    
    def check_status(self, job_id):
        """Check job status on RunPod"""
        try:
            response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Status check failed: {response.status_code}")
                return 'FAILED', None
            
            result = response.json()
            status = result.get('status', 'UNKNOWN')
            
            logger.info(f"Job {job_id} status: {status}")
            
            if status == 'COMPLETED':
                output = result.get('output')
                if output and 'images' in output and output['images']:
                    return 'COMPLETED', output['images'][0]
                else:
                    logger.error(f"No images in completed job output: {output}")
                    return 'FAILED', None
            elif status in ['FAILED', 'CANCELLED', 'TIMED_OUT']:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Job failed: {error_msg}")
                return 'FAILED', error_msg
            else:
                # Still running
                return status, None
                
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return 'FAILED', str(e)
    
    def wait_for_completion(self, job_id, timeout=300):
        """Wait for job completion with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status, result = self.check_status(job_id)
            
            if status == 'COMPLETED':
                return True, result
            elif status == 'FAILED':
                return False, result
            
            # Wait before next check
            time.sleep(5)
        
        logger.error(f"Job {job_id} timed out after {timeout} seconds")
        return False, "Generation timed out"
    
    def base64_to_image(self, base64_string):
        """Convert base64 string to PIL Image"""
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error converting base64 to image: {e}")
            return None
    
    def save_result_image(self, base64_image, output_path):
        """Save base64 image to file"""
        try:
            image = self.base64_to_image(base64_image)
            if image:
                image.save(output_path, 'PNG')
                logger.info(f"Result saved to: {output_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving result image: {e}")
            return False
    
    def test_connection(self):
        """Test connection to RunPod serverless endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Test function
def test_simple_workflow():
    """Test the simple workflow"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    API_KEY = os.getenv('RUNPOD_API_KEY')
    ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', 'psl-morph')
    
    if not API_KEY:
        print("Please set RUNPOD_API_KEY in .env file")
        return
    
    client = RunPodClient(API_KEY, ENDPOINT_ID)
    
    # Test with a sample image
    test_image_path = "uploads/test_image.jpg"  # Replace with actual path
    
    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        return
    
    # Test HTN preset with medium denoise intensity
    result, error = client.generate_image(test_image_path, 'HTN', 5)
    
    if error:
        print(f"Error: {error}")
        return
    
    if isinstance(result, str) and result.startswith('data:'):
        # Direct base64 result
        print("Generation completed immediately!")
        client.save_result_image(result, "outputs/test_result.png")
    else:
        # Job ID - wait for completion
        print(f"Job submitted: {result}")
        success, final_result = client.wait_for_completion(result)
        
        if success:
            print("Generation completed!")
            client.save_result_image(final_result, "outputs/test_result.png")
        else:
            print(f"Generation failed: {final_result}")

if __name__ == "__main__":
    test_simple_workflow()
