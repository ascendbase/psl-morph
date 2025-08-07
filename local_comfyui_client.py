"""
Local ComfyUI Client for Face Morphing App
Uses the specific workflow_facedetailer.json workflow
"""

import requests
import json
import time
import uuid
import logging
import os
import random
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class LocalComfyUIClient:
    def __init__(self, base_url="http://127.0.0.1:8188", workflow_path="comfyui_workflows/workflow_facedetailer.json", timeout=300):
        """Initialize Local ComfyUI client"""
        self.base_url = base_url.rstrip('/')
        self.workflow_path = workflow_path
        self.timeout = timeout
        self.workflow_template = None
        self.load_workflow_template()
        logger.info(f"Local ComfyUI Client initialized: {self.base_url}")
        logger.info(f"Using workflow: {self.workflow_path}")
    
    def load_workflow_template(self):
        """Load the workflow template from file"""
        try:
            with open(self.workflow_path, 'r') as f:
                self.workflow_template = json.load(f)
            logger.info(f"Loaded workflow template from {self.workflow_path}")
        except Exception as e:
            logger.error(f"Failed to load workflow template: {e}")
            self.workflow_template = None
    
    def test_connection(self):
        """Test connection to ComfyUI"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            if response.status_code == 200:
                logger.info("ComfyUI connection successful")
                return True
            else:
                logger.warning(f"ComfyUI connection failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"ComfyUI connection test failed: {e}")
            return False
    
    def generate_image(self, image_path, preset_name, denoise_strength):
        """
        Generate face morphing image using local ComfyUI
        
        Args:
            image_path: Path to input image
            preset_name: HTN, Chadlite, or Chad (for logging)
            denoise_strength: Denoise strength (0.10-0.25)
            
        Returns:
            prompt_id: ComfyUI prompt ID for tracking
        """
        try:
            # Test connection first
            if not self.test_connection():
                logger.error("Cannot connect to local ComfyUI")
                return None
            
            # Upload the image to ComfyUI
            if not self.upload_image(image_path):
                logger.error("Failed to upload image to ComfyUI")
                return None
            
            # Prepare the workflow with the uploaded image
            workflow = self._prepare_workflow(image_path, denoise_strength, preset_name)
            if not workflow:
                logger.error("Failed to prepare workflow")
                return None
            
            # Queue the workflow
            prompt_id = self.queue_workflow(workflow)
            if prompt_id:
                logger.info(f"Started local ComfyUI generation: {prompt_id} (preset: {preset_name}, denoise: {denoise_strength})")
                return prompt_id
            else:
                logger.error("Failed to queue workflow")
                return None
                
        except Exception as e:
            logger.error(f"Local ComfyUI generation failed: {e}")
            return None
    
    def queue_workflow(self, workflow):
        """Queue a workflow in ComfyUI"""
        try:
            prompt_id = str(uuid.uuid4())
            payload = {
                "prompt": workflow,
                "client_id": prompt_id
            }
            
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            actual_prompt_id = result.get('prompt_id', prompt_id)
            logger.info(f"Workflow queued successfully: {actual_prompt_id}")
            return actual_prompt_id
            
        except Exception as e:
            logger.error(f"Failed to queue workflow: {e}")
            return None
    
    def get_job_status(self, prompt_id):
        """Get job status"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id in history:
                # Check if the job completed successfully
                job_data = history[prompt_id]
                if 'outputs' in job_data and job_data['outputs']:
                    logger.info(f"Job {prompt_id} completed successfully")
                    return "COMPLETED"
                else:
                    logger.warning(f"Job {prompt_id} completed but no outputs found")
                    return "FAILED"
            else:
                # Check queue status
                queue_response = requests.get(f"{self.base_url}/queue", timeout=10)
                if queue_response.status_code == 200:
                    queue_data = queue_response.json()
                    
                    # Check if job is in running queue
                    for item in queue_data.get('queue_running', []):
                        if item[1] == prompt_id:
                            logger.info(f"Job {prompt_id} is currently running")
                            return "IN_PROGRESS"
                    
                    # Check if job is in pending queue
                    for item in queue_data.get('queue_pending', []):
                        if item[1] == prompt_id:
                            logger.info(f"Job {prompt_id} is pending")
                            return "IN_PROGRESS"
                
                logger.info(f"Job {prompt_id} status unknown, assuming in progress")
                return "IN_PROGRESS"
                
        except Exception as e:
            logger.error(f"Status check failed for {prompt_id}: {e}")
            return "FAILED"
    
    def get_job_output(self, prompt_id):
        """Get job output"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id not in history:
                logger.error(f"Job {prompt_id} not found in history")
                return None
            
            # Find output images
            outputs = history[prompt_id].get('outputs', {})
            
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
                        
                        img_response = requests.get(f"{self.base_url}/view", params=params, timeout=30)
                        img_response.raise_for_status()
                        
                        logger.info(f"Successfully retrieved output image for {prompt_id}: {filename}")
                        return img_response.content
            
            logger.error(f"No output images found for job {prompt_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job output for {prompt_id}: {e}")
            return None
    
    def upload_image(self, image_path):
        """Upload image to ComfyUI input folder"""
        try:
            filename = os.path.basename(image_path)
            
            with open(image_path, 'rb') as f:
                files = {
                    'image': (filename, f, 'image/jpeg'),
                    'overwrite': (None, 'true')
                }
                response = requests.post(f"{self.base_url}/upload/image", files=files, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Uploaded image to ComfyUI: {filename}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return False
    
    def _prepare_workflow(self, image_path, denoise_strength, preset_name):
        """Prepare ComfyUI workflow using the loaded template"""
        try:
            if not self.workflow_template:
                logger.error("No workflow template loaded")
                return None
            
            # Create a copy of the template
            workflow = json.loads(json.dumps(self.workflow_template))
            
            # Get image filename
            image_filename = os.path.basename(image_path)
            
            # Generate unique seed for each run
            unique_seed = random.randint(1, 2**32 - 1)
            timestamp = int(time.time())
            
            # Update the workflow with our parameters
            
            # Update LoadImage node (node 5) with the uploaded image
            if "5" in workflow:
                workflow["5"]["inputs"]["image"] = image_filename
                logger.info(f"Set input image to: {image_filename}")
            
            # Update FaceDetailer node (node 8) with denoise strength and seed
            if "8" in workflow:
                workflow["8"]["inputs"]["denoise"] = denoise_strength
                workflow["8"]["inputs"]["seed"] = unique_seed
                logger.info(f"Set denoise to {denoise_strength} and seed to {unique_seed}")
            
            # Update SaveImage node (node 9) with custom filename
            if "9" in workflow:
                workflow["9"]["inputs"]["filename_prefix"] = f"morph_{preset_name}_{timestamp}"
                logger.info(f"Set output filename prefix to: morph_{preset_name}_{timestamp}")
            
            logger.info(f"Prepared workflow for {preset_name} with denoise {denoise_strength}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to prepare workflow: {e}")
            return None
    
    def clear_queue(self):
        """Clear ComfyUI queue"""
        try:
            response = requests.post(f"{self.base_url}/queue", json={"clear": True}, timeout=10)
            if response.status_code == 200:
                logger.info("Cleared ComfyUI queue")
                return True
            else:
                logger.warning(f"Failed to clear queue: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Could not clear ComfyUI queue: {e}")
            return False
