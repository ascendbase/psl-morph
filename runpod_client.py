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