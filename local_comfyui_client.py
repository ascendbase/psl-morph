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
from cloudflare_tunnel_detector import get_dynamic_comfyui_url

logger = logging.getLogger(__name__)

class LocalComfyUIClient:
    def __init__(self, base_url=None, workflow_path="comfyui_workflows/workflow_facedetailer.json", timeout=300):
        """Initialize Local ComfyUI client"""
        # Use dynamic URL detection if no base_url provided
        if base_url is None:
            self.base_url = get_dynamic_comfyui_url().rstrip('/')
        else:
            self.base_url = base_url.rstrip('/')
        self.workflow_path = workflow_path
        self.timeout = timeout
        self.workflow_template = None
        self.feature_workflows = {}
        self.supported_features = {
            'eyes': {
                'workflow': 'comfyui_workflows/workflow_custom_eyes.json',
                'area': 'eyes',
                'prompt': 'chad, male model',
                'grow': 8,
                'blur': 4
            },
            'eyebrows': {
                'workflow': 'comfyui_workflows/workflow_faceanalysis_eyebrows.json',
                'area': 'eyebrows',
                'prompt': 'chad, male model',
                'grow': 6,
                'blur': 3
            },
            'nose': {
                'workflow': 'comfyui_workflows/workflow_custom_nose.json',
                'area': 'nose',
                'prompt': 'chad, male model',
                'grow': 10,
                'blur': 5
            },
            'mouth': {
                'workflow': 'comfyui_workflows/workflow_custom_mouth.json',
                'area': 'mouth',
                'prompt': 'chad, male model',
                'grow': 12,
                'blur': 6
            },
            'skull': {
                'workflow': 'comfyui_workflows/workflow_custom_skull.json',
                'area': 'skull',
                'prompt': 'chad, male model',
                'grow': 0,
                'blur': 0,
                'denoise': 0.25
            }
        }
        self.load_workflow_template()
        self.load_feature_workflows()
        logger.info(f"Local ComfyUI Client initialized: {self.base_url}")
        logger.info(f"Default workflow: {self.workflow_path}")
        logger.info(f"Supported features: {', '.join(self.supported_features.keys())}")
    
    def load_workflow_template(self):
        """Load the workflow template from file"""
        try:
            with open(self.workflow_path, 'r') as f:
                self.workflow_template = json.load(f)
            logger.info(f"Loaded workflow template from {self.workflow_path}")
        except Exception as e:
            logger.error(f"Failed to load workflow template: {e}")
            self.workflow_template = None
    
    def load_feature_workflows(self):
        """Load feature-specific workflows"""
        for feature, config in self.supported_features.items():
            file_path = config['workflow']
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        self.feature_workflows[feature] = json.load(f)
                    logger.info(f"Loaded {feature} workflow from {file_path}")
                else:
                    logger.warning(f"Feature workflow not found: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {feature} workflow: {e}")
        
        logger.info(f"Loaded {len(self.feature_workflows)} feature-specific workflows")
    
    def test_connection(self):
        """Test connection to ComfyUI"""
        try:
            # Update base_url with latest detected URL
            self.base_url = get_dynamic_comfyui_url().rstrip('/')
            
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            if response.status_code == 200:
                logger.info(f"ComfyUI connection successful: {self.base_url}")
                return True
            else:
                logger.warning(f"ComfyUI connection failed with status: {response.status_code} at {self.base_url}")
                return False
        except Exception as e:
            logger.error(f"ComfyUI connection test failed: {e} (URL: {self.base_url})")
            return False
    
    def generate_image(self, image_path, preset_name, denoise_strength, selected_features=None):
        """
        Generate face morphing image using local ComfyUI
        
        Args:
            image_path: Path to input image
            preset_name: HTN, Chadlite, or Chad (for logging)
            denoise_strength: Denoise strength (0.10-0.25)
            selected_features: List of features for custom mode (e.g., ['eyes', 'nose'])
            
        Returns:
            prompt_id: ComfyUI prompt ID for tracking
        """
        try:
            # Update URL and test connection first
            self.base_url = get_dynamic_comfyui_url().rstrip('/')
            if not self.test_connection():
                logger.error(f"Cannot connect to ComfyUI at {self.base_url}")
                return None
            
            # Upload the image to ComfyUI
            if not self.upload_image(image_path):
                logger.error("Failed to upload image to ComfyUI")
                return None
            
            # Prepare the workflow with the uploaded image
            workflow = self._prepare_workflow(image_path, denoise_strength, preset_name, selected_features)
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
        """Get job output - prioritizes final result nodes"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id not in history:
                logger.error(f"Job {prompt_id} not found in history")
                return None
            
            # Find output images
            outputs = history[prompt_id].get('outputs', {})
            
            # Priority order for output nodes:
            # 1. Node 10 - "Save final result" (custom features with compositing)
            # 2. Node 9 - "Save Image" (default workflow)
            # 3. Any other node with images (fallback)
            
            priority_nodes = ["10", "9"]
            
            # First, try priority nodes
            for priority_node in priority_nodes:
                if priority_node in outputs and 'images' in outputs[priority_node]:
                    for image_info in outputs[priority_node]['images']:
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
                        
                        logger.info(f"Successfully retrieved output image from node {priority_node} for {prompt_id}: {filename}")
                        return img_response.content
            
            # Fallback: try any node with images
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
                        
                        logger.info(f"Successfully retrieved output image from fallback node {node_id} for {prompt_id}: {filename}")
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
    
    def _prepare_workflow(self, image_path, denoise_strength, preset_name, selected_features=None):
        """Prepare ComfyUI workflow using feature-specific workflows"""
        try:
            # Get image filename
            image_filename = os.path.basename(image_path)
            
            # Generate unique seed for each run
            unique_seed = random.randint(1, 2**32 - 1)
            timestamp = int(time.time())
            
            # Check for CHAD 2.0 mode first
            if preset_name == "CHAD_2_0":
                chad_2_0_workflow_path = "comfyui_workflows/workflow_chad_2_0.json"
                if os.path.exists(chad_2_0_workflow_path):
                    with open(chad_2_0_workflow_path, 'r') as f:
                        workflow = json.load(f)
                    actual_denoise = denoise_strength
                    logger.info(f"Using CHAD 2.0 workflow with SD XL + custom LoRA, denoise {denoise_strength}")
                else:
                    logger.error(f"CHAD 2.0 workflow not found: {chad_2_0_workflow_path}")
                    return None
            # For selected features, use feature-specific workflows
            elif selected_features and len(selected_features) == 1:
                feature = selected_features[0]
                if feature in self.feature_workflows:
                    workflow = json.loads(json.dumps(self.feature_workflows[feature]))
                    # Use per-feature denoise if provided, default to 0.3 for backward compatibility
                    actual_denoise = self.supported_features.get(feature, {}).get('denoise', 0.3)
                    logger.info(f"Using feature-specific workflow for {feature} with denoise {actual_denoise}")
                else:
                    logger.error(f"No workflow found for feature: {feature}")
                    return None
            else:
                # Use default workflow for full face or multiple features
                if not self.workflow_template:
                    logger.error("No default workflow template loaded")
                    return None
                workflow = json.loads(json.dumps(self.workflow_template))
                actual_denoise = denoise_strength
                logger.info(f"Using default workflow with denoise {denoise_strength}")
            
            # Update LoadImage node (node 5) with the uploaded image
            if "5" in workflow:
                workflow["5"]["inputs"]["image"] = image_filename
                logger.info(f"Set input image to: {image_filename}")
            
            # Update FaceSegmentation node (node 6) with feature-specific parameters
            if selected_features and len(selected_features) == 1:
                feature = selected_features[0]
                if feature in self.supported_features and "6" in workflow:
                    feature_config = self.supported_features[feature]
                    workflow["6"]["inputs"]["area"] = feature_config["area"]
                    workflow["6"]["inputs"]["grow"] = feature_config["grow"]
                    workflow["6"]["inputs"]["blur"] = feature_config["blur"]
                    logger.info(f"Updated FaceSegmentation for {feature}: area={feature_config['area']}, grow={feature_config['grow']}, blur={feature_config['blur']}")
            
            # Update FaceDetailer node (node 8) with denoise strength and seed
            if "8" in workflow:
                workflow["8"]["inputs"]["denoise"] = actual_denoise
                workflow["8"]["inputs"]["seed"] = unique_seed
                logger.info(f"Set FaceDetailer denoise to {actual_denoise} and seed to {unique_seed}")
            
            # Update SaveImage node with custom filename
            # For custom features (node 10), for default workflow (node 9)
            save_node = "10" if selected_features and len(selected_features) == 1 else "9"
            if save_node in workflow:
                if selected_features:
                    features_str = '_'.join(selected_features)
                    workflow[save_node]["inputs"]["filename_prefix"] = f"morph_{features_str}_{timestamp}"
                    logger.info(f"Set output filename prefix in node {save_node} to: morph_{features_str}_{timestamp}")
                else:
                    workflow[save_node]["inputs"]["filename_prefix"] = f"morph_{preset_name}_{timestamp}"
                    logger.info(f"Set output filename prefix in node {save_node} to: morph_{preset_name}_{timestamp}")
            
            if selected_features:
                logger.info(f"Prepared workflow for features {', '.join(selected_features)} with denoise {actual_denoise}")
            else:
                logger.info(f"Prepared workflow for {preset_name} with denoise {actual_denoise}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to prepare workflow: {e}")
            return None
    
    def generate_image_with_features(self, image_path, selected_features, denoise_strength=0.3):
        """
        Generate image with specific features selected
        
        Args:
            image_path: Path to input image
            selected_features: List of features to modify (e.g., ['eyes', 'nose'])
            denoise_strength: Denoise strength (default 0.3 for features)
            
        Returns:
            prompt_id: ComfyUI prompt ID for tracking
        """
        logger.info(f"Starting feature-specific generation for features: {', '.join(selected_features)}")
        return self.generate_image(
            image_path=image_path,
            preset_name="Custom_Features",
            denoise_strength=denoise_strength,
            selected_features=selected_features
        )
    
    def generate_image_with_face_swap(self, original_image_path, reference_image_path, swap_intensity="50%"):
        """
        Generate image using face swap workflow
        
        Args:
            original_image_path: Path to original user image
            reference_image_path: Path to reference chad image
            swap_intensity: Face swap intensity as percentage string (e.g., "50%")
            
        Returns:
            prompt_id: ComfyUI prompt ID for tracking
        """
        try:
            # Update URL and test connection first
            self.base_url = get_dynamic_comfyui_url().rstrip('/')
            if not self.test_connection():
                logger.error(f"Cannot connect to ComfyUI at {self.base_url}")
                return None
            
            # Load clean face swap workflow
            face_swap_workflow_path = "comfyui_workflows/face_swap_with_intensity_clean.json"
            if not os.path.exists(face_swap_workflow_path):
                logger.error(f"Face swap workflow not found: {face_swap_workflow_path}")
                return None
            
            with open(face_swap_workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Upload both images to ComfyUI
            if not self.upload_image(original_image_path):
                logger.error("Failed to upload original image to ComfyUI")
                return None
            
            if not self.upload_image(reference_image_path):
                logger.error("Failed to upload reference image to ComfyUI")
                return None
            
            # Get filenames
            original_filename = os.path.basename(original_image_path)
            reference_filename = os.path.basename(reference_image_path)
            
            # Generate unique timestamp
            timestamp = int(time.time())
            
            # Update the clean workflow with our images and settings
            # Node 1: Original image (Load Original Image)
            workflow["1"]["inputs"]["image"] = original_filename
            logger.info(f"Set original image in node 1: {original_filename}")
            
            # Node 2: Source image (Load Source Face Image)  
            workflow["2"]["inputs"]["image"] = reference_filename
            logger.info(f"Set reference image in node 2: {reference_filename}")
            
            # Node 3: Set face swap intensity (ReActorSetWeight)
            workflow["3"]["inputs"]["faceswap_weight"] = swap_intensity
            logger.info(f"Set face swap intensity in node 3: {swap_intensity}")
            
            # Node 5: Set output filename (SaveImage)
            workflow["5"]["inputs"]["filename_prefix"] = f"face_swap_{timestamp}"
            logger.info(f"Set output filename prefix in node 5: face_swap_{timestamp}")
            
            # Queue the workflow
            prompt_id = self.queue_workflow(workflow)
            if prompt_id:
                logger.info(f"Started face swap generation: {prompt_id} (intensity: {swap_intensity})")
                return prompt_id
            else:
                logger.error("Failed to queue face swap workflow")
                return None
                
        except Exception as e:
            logger.error(f"Face swap generation failed: {e}")
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
