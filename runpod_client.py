"""
RunPod Serverless Client for Stable Diffusion XL
"""

import requests
import json
import base64
import time
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
    
    def prepare_comfyui_workflow(self, image_path, denoise_strength, preset_name):
        """Prepare ComfyUI workflow for face morphing"""
        try:
            import os
            import random
            
            # Get image filename
            image_filename = os.path.basename(image_path)
            
            # Generate unique seed for each run
            unique_seed = random.randint(1, 2**32 - 1)
            timestamp = int(time.time())
            
            # Use FaceDetailer workflow for better face morphing
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
                        "model": ["1", 0],
                        "clip": ["1", 1],
                        "lora_name": "chad_sd1.5.safetensors",
                        "strength_model": 0.8,
                        "strength_clip": 0.85
                    },
                    "class_type": "LoraLoader",
                    "_meta": {
                        "title": "Load LoRA"
                    }
                },
                "3": {
                    "inputs": {
                        "text": "chad, male model, face portrait",
                        "clip": ["2", 1]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {
                        "title": "CLIP Text Encode (Prompt)"
                    }
                },
                "4": {
                    "inputs": {
                        "text": "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face",
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
                        "title": "Load Original Image"
                    }
                },
                "6": {
                    "inputs": {
                        "model_name": "bbox/face_yolov8m.pt"
                    },
                    "class_type": "UltralyticsDetectorProvider",
                    "_meta": {
                        "title": "Face Detector"
                    }
                },
                "7": {
                    "inputs": {
                        "model_name": "sam_vit_b_01ec64.pth",
                        "device_mode": "AUTO"
                    },
                    "class_type": "SAMLoader",
                    "_meta": {
                        "title": "SAM Loader"
                    }
                },
                "8": {
                    "inputs": {
                        "image": ["5", 0],
                        "model": ["2", 0],
                        "clip": ["2", 1],
                        "vae": ["1", 2],
                        "positive": ["3", 0],
                        "negative": ["4", 0],
                        "bbox_detector": ["6", 0],
                        "sam_model_opt": ["7", 0],
                        "segm_detector_opt": None,
                        "detailer_hook": None,
                        "scheduler_func_opt": None,
                        "wildcard": "",
                        "guide_size": 512,
                        "guide_size_for": "bbox",
                        "max_size": 1024,
                        "seed": unique_seed,
                        "steps": 20,
                        "cfg": 8.0,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": denoise_strength,
                        "feather": 5,
                        "noise_mask": True,
                        "force_inpaint": True,
                        "bbox_threshold": 0.50,
                        "bbox_dilation": 10,
                        "bbox_crop_factor": 3.0,
                        "sam_detection_hint": "center-1",
                        "sam_dilation": 0,
                        "sam_threshold": 0.93,
                        "sam_bbox_expansion": 0,
                        "sam_mask_hint_threshold": 0.70,
                        "sam_mask_hint_use_negative": "False",
                        "drop_size": 10,
                        "cycle": 1,
                        "inpaint_model": False,
                        "noise_mask_feather": 20
                    },
                    "class_type": "FaceDetailer",
                    "_meta": {
                        "title": "Face Detailer"
                    }
                },
                "9": {
                    "inputs": {
                        "filename_prefix": f"morph_{preset_name}_{timestamp}",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage",
                    "_meta": {
                        "title": "Save Result"
                    }
                }
            }
            
            logger.info(f"Prepared FaceDetailer workflow for {preset_name} with denoise {denoise_strength} and seed {unique_seed}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to prepare workflow: {e}")
            return None
    
    def upload_image_to_serverless(self, image_path):
        """Upload image to serverless endpoint"""
        try:
            # For serverless, we'll send the image as base64 in the payload
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_image
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None
    
    def base64_to_image(self, base64_string):
        """Convert base64 string to PIL Image"""
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error converting base64 to image: {e}")
            return None
    
    def create_face_morph_payload(self, image_path, preset_key, presets):
        """Create payload for face morphing with SDXL"""
        
        # Convert image to base64
        image_base64 = self.image_to_base64(image_path)
        if not image_base64:
            return None
        
        preset = presets[preset_key]
        
        # Face morphing prompts based on preset
        prompts = {
            'HTN': "portrait of a handsome man, masculine features, strong jawline, confident expression, professional lighting, high quality, detailed",
            'Chadlite': "portrait of a very attractive man, chiseled features, strong masculine jawline, piercing eyes, confident smile, professional photography, ultra detailed, high quality",
            'Chad': "portrait of an extremely handsome alpha male, perfect masculine features, strong square jaw, intense eyes, confident expression, professional model lighting, ultra realistic, 8k quality"
        }
        
        negative_prompt = "ugly, deformed, disfigured, poor quality, blurry, distorted, bad anatomy, bad proportions, extra limbs, cloned face, malformed, gross proportions, missing arms, missing legs, extra arms, extra legs, mutated hands, long neck, cross-eyed, mutated, mutation, bad hands, bad fingers"
        
        payload = {
            "input": {
                "prompt": prompts.get(preset_key, prompts['HTN']),
                "negative_prompt": negative_prompt,
                "image": image_base64,
                "strength": preset['denoise'],  # Use denoise as strength for img2img
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 768,
                "height": 768,
                "seed": -1,  # Random seed
                "scheduler": "DPMSolverMultistepScheduler"
            }
        }
        
        return payload
    
    def run_generation(self, image_path, preset_key, presets):
        """Run face morphing generation on RunPod"""
        
        # Create payload
        payload = self.create_face_morph_payload(image_path, preset_key, presets)
        if not payload:
            return None, "Failed to prepare image"
        
        try:
            # Submit job
            logger.info(f"Submitting RunPod job for {preset_key} preset")
            response = requests.post(
                f"{self.base_url}/run",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"RunPod submission failed: {response.status_code} - {response.text}")
                return None, f"RunPod error: {response.status_code}"
            
            result = response.json()
            job_id = result.get('id')
            
            if not job_id:
                logger.error(f"No job ID returned: {result}")
                return None, "No job ID returned from RunPod"
            
            logger.info(f"RunPod job submitted: {job_id}")
            return job_id, None
            
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
                if output and 'image' in output:
                    return 'COMPLETED', output['image']
                else:
                    logger.error(f"No image in completed job output: {output}")
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
    
    def generate_image(self, image_path, denoise_strength, preset_name):
        """Generate face morphing using RunPod serverless endpoint with ComfyUI workflow"""
        try:
            # Prepare workflow
            workflow = self.prepare_comfyui_workflow(image_path, denoise_strength, preset_name)
            if not workflow:
                logger.error("Failed to prepare workflow")
                return None, "Failed to prepare workflow"
            
            # Convert image to base64 for upload
            image_base64 = self.image_to_base64(image_path)
            if not image_base64:
                logger.error("Failed to convert image to base64")
                return None, "Failed to process image"
            
            # Prepare payload for serverless endpoint with ComfyUI workflow
            payload = {
                "input": {
                    "workflow": workflow,
                    "images": {
                        "LoadImage_5": image_base64  # Node 5 is LoadImage in our workflow
                    }
                }
            }
            
            # Submit job to serverless endpoint
            logger.info(f"Submitting RunPod serverless job for {preset_name} preset")
            response = requests.post(
                f"{self.base_url}/run",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"RunPod submission failed: {response.status_code} - {response.text}")
                return None, f"RunPod error: {response.status_code}"
            
            result = response.json()
            job_id = result.get('id')
            
            if not job_id:
                logger.error(f"No job ID returned: {result}")
                return None, "No job ID returned from RunPod"
            
            logger.info(f"RunPod serverless job submitted: {job_id}")
            return job_id, None
            
        except Exception as e:
            logger.error(f"RunPod serverless submission error: {e}")
            return None, str(e)
    
    def get_job_status(self, job_id):
        """Check job status on RunPod serverless"""
        try:
            response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Status check failed: {response.status_code}")
                return 'FAILED'
            
            result = response.json()
            status = result.get('status', 'UNKNOWN')
            
            logger.info(f"Job {job_id} status: {status}")
            
            if status == 'COMPLETED':
                output = result.get('output')
                if output:
                    return 'COMPLETED'
                else:
                    logger.error(f"No output in completed job: {result}")
                    return 'FAILED'
            elif status in ['FAILED', 'CANCELLED', 'TIMED_OUT']:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Job failed: {error_msg}")
                return 'FAILED'
            else:
                # Still running
                return status
                
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return 'FAILED'
    
    def get_job_output(self, job_id):
        """Get job output from RunPod serverless"""
        try:
            # Get full job result
            response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get job status: {response.status_code}")
                return None
            
            result = response.json()
            if result.get('status') != 'COMPLETED':
                logger.error(f"Job not completed: {result.get('status')}")
                return None
            
            # Extract output image from result
            output = result.get('output')
            if output and 'images' in output:
                # If output contains base64 images directly
                return base64.b64decode(output['images'][0])
            elif output and 'image_url' in output:
                # If output contains image URL
                img_response = requests.get(output['image_url'], timeout=30)
                img_response.raise_for_status()
                return img_response.content
            else:
                logger.error(f"No image found in output: {output}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get job output: {e}")
            return None
    
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
def test_runpod_client():
    """Test the RunPod client with dummy data"""
    # You'll need to set these
    API_KEY = "your_runpod_api_key_here"
    ENDPOINT_ID = "your_endpoint_id_here"
    
    client = RunPodClient(API_KEY, ENDPOINT_ID)
    
    # Test with a sample image
    test_image_path = "uploads/test_image.jpg"  # Replace with actual path
    
    presets = {
        'HTN': {'denoise': 0.3},
        'Chadlite': {'denoise': 0.5}, 
        'Chad': {'denoise': 0.7}
    }
    
    job_id, error = client.run_generation(test_image_path, 'HTN', presets)
    
    if error:
        print(f"Error: {error}")
        return
    
    print(f"Job submitted: {job_id}")
    
    # Wait for completion
    success, result = client.wait_for_completion(job_id)
    
    if success:
        print("Generation completed!")
        client.save_result_image(result, "outputs/test_result.png")
    else:
        print(f"Generation failed: {result}")

if __name__ == "__main__":
    test_runpod_client()
