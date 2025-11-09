"""
ComfyUI Client for Face Morphing App
Handles communication with ComfyUI API
"""

import requests
import json
import time
import uuid
import logging
from io import BytesIO
from PIL import Image
import base64

logger = logging.getLogger(__name__)

class ComfyUIClient:
    def __init__(self, base_url="http://127.0.0.1:8188", timeout=300):
        """Initialize ComfyUI client"""
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        logger.info(f"ComfyUI Client initialized: {self.base_url}")
    
    def test_connection(self):
        """Test connection to ComfyUI"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def generate_image(self, image_path, preset_name, denoise_strength):
        """
        Generate face morphing image
        
        Args:
            image_path: Path to input image
            preset_name: HTN, Chadlite, or Chad
            denoise_strength: Denoise strength (0.2-0.8)
            
        Returns:
            prompt_id: ComfyUI prompt ID for tracking
        """
        try:
            # First, upload the image to ComfyUI
            if not self.upload_image(image_path):
                logger.error("Failed to upload image to ComfyUI")
                return None
            
            # Load and prepare the workflow
            workflow = self._prepare_workflow(image_path, denoise_strength, preset_name)
            if not workflow:
                logger.error("Failed to prepare workflow")
                return None
            
            # Queue the workflow
            prompt_id = self.queue_workflow(workflow)
            if prompt_id:
                logger.info(f"Started generation: {prompt_id}")
                return prompt_id
            else:
                logger.error("Failed to queue workflow")
                return None
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
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
            return result.get('prompt_id', prompt_id)
            
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
                return "COMPLETED"
            else:
                return "IN_PROGRESS"
                
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return "FAILED"
    
    def get_job_output(self, prompt_id):
        """Get job output"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id not in history:
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
                        
                        return img_response.content
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job output: {e}")
            return None
    
    def upload_image(self, image_path):
        """Upload image to ComfyUI input folder"""
        try:
            import os
            filename = os.path.basename(image_path)
            
            with open(image_path, 'rb') as f:
                files = {
                    'image': (filename, f, 'image/jpeg'),
                    'overwrite': (None, 'true')
                }
                response = requests.post(f"{self.base_url}/upload/image", files=files, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Uploaded image to ComfyUI: {filename} -> {result}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return False
    
    def _prepare_workflow(self, image_path, denoise_strength, preset_name):
        """Load and prepare the actual workflow_facedetailer.json with correct parameters"""
        try:
            import os
            import random
            
            # Get image filename
            image_filename = os.path.basename(image_path)
            
            # Generate unique seed for each run
            unique_seed = random.randint(1, 2**32 - 1)
            timestamp = int(time.time())
            
            # Load the actual workflow file
            workflow_path = os.path.join(os.path.dirname(__file__), 'comfyui_workflows', 'workflow_facedetailer.json')
            
            if not os.path.exists(workflow_path):
                logger.error(f"Workflow file not found: {workflow_path}")
                return None
            
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Update the workflow with our parameters
            
            # Update image filename (node 5)
            if "5" in workflow:
                workflow["5"]["inputs"]["image"] = image_filename
            
            # Update seed and denoise strength (node 8 - FaceDetailer)
            if "8" in workflow:
                workflow["8"]["inputs"]["seed"] = unique_seed
                workflow["8"]["inputs"]["denoise"] = denoise_strength
            
            # Update output filename (node 9)
            if "9" in workflow:
                workflow["9"]["inputs"]["filename_prefix"] = f"morph_{preset_name}_{timestamp}"
            
            logger.info(f"Loaded workflow_facedetailer.json for {preset_name} with denoise {denoise_strength} and seed {unique_seed}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to prepare workflow: {e}")
            return None
    
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
            import os
            import random
            
            # Upload both images to ComfyUI
            if not self.upload_image(original_image_path):
                logger.error("Failed to upload original image to ComfyUI")
                return None
            
            if not self.upload_image(reference_image_path):
                logger.error("Failed to upload reference image to ComfyUI")
                return None
            
            # Load face swap workflow
            face_swap_workflow_path = os.path.join(os.path.dirname(__file__), 'comfyui_workflows', 'face_swap_with_intensity.json')
            if not os.path.exists(face_swap_workflow_path):
                logger.error(f"Face swap workflow not found: {face_swap_workflow_path}")
                return None
            
            with open(face_swap_workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Get filenames
            original_filename = os.path.basename(original_image_path)
            reference_filename = os.path.basename(reference_image_path)
            
            # Generate unique seed and timestamp
            unique_seed = random.randint(1, 2**32 - 1)
            timestamp = int(time.time())
            
            # Convert nodes array format to direct node dict format that ComfyUI expects
            if "nodes" in workflow:
                logger.info("Converting nodes array format to direct node dict format")
                
                # Convert from nodes array format to direct node dict format
                nodes_list = workflow["nodes"]
                new_workflow = {}
                
                original_image_set = False
                source_image_set = False
                
                for node in nodes_list:
                    if not isinstance(node, dict):
                        continue
                    
                    node_id = str(node.get("id"))
                    
                    # Convert node structure
                    new_node = {
                        "class_type": node.get("type"),  # Convert "type" to "class_type"
                        "inputs": {}
                    }
                    
                    # Handle LoadImage nodes specially
                    if node.get("type") == "LoadImage":
                        title = node.get("title", "").lower()
                        
                        # Set the image input based on title
                        if "original" in title and not original_image_set:
                            new_node["inputs"]["image"] = original_filename
                            logger.info(f"Set original image in converted node {node_id}: {original_filename}")
                            original_image_set = True
                        elif "source" in title and not source_image_set:
                            new_node["inputs"]["image"] = reference_filename
                            logger.info(f"Set reference image in converted node {node_id}: {reference_filename}")
                            source_image_set = True
                        else:
                            # Use the original widgets_values if available
                            if "widgets_values" in node and len(node["widgets_values"]) > 0:
                                new_node["inputs"]["image"] = node["widgets_values"][0]
                        
                        # Set upload input
                        new_node["inputs"]["upload"] = "image"
                    
                    # Handle ReActorSetWeight nodes
                    elif node.get("type") == "ReActorSetWeight":
                        # Convert widgets_values to inputs
                        if "widgets_values" in node and len(node["widgets_values"]) > 0:
                            new_node["inputs"]["faceswap_weight"] = swap_intensity
                            logger.info(f"Set face swap intensity in converted ReActorSetWeight node {node_id}: {swap_intensity}")
                    
                    # Handle SaveImage nodes
                    elif node.get("type") == "SaveImage":
                        new_node["inputs"]["filename_prefix"] = f"face_swap_{timestamp}"
                        logger.info(f"Set output filename prefix in converted SaveImage node {node_id}: face_swap_{timestamp}")
                    
                    # Handle other node types - copy inputs from the original node structure
                    if "inputs" in node:
                        for input_name, input_data in node["inputs"].items():
                            if isinstance(input_data, dict) and "link" in input_data:
                                # This is a connection, keep the link
                                new_node["inputs"][input_name] = input_data["link"]
                            else:
                                # This is a direct value
                                new_node["inputs"][input_name] = input_data
                    
                    # Copy widgets_values to inputs for other node types
                    if "widgets_values" in node and node.get("type") not in ["LoadImage", "ReActorSetWeight", "SaveImage"]:
                        # Map common widget values to input names based on node type
                        if node.get("type") == "ReActorFaceSwap":
                            widget_names = ["enabled", "swap_model", "facedetection", "face_restore_model", 
                                          "face_restore_visibility", "codeformer_weight", "detect_gender_input",
                                          "detect_gender_source", "input_faces_index", "source_faces_index", "console_log_level"]
                            for i, value in enumerate(node["widgets_values"]):
                                if i < len(widget_names):
                                    new_node["inputs"][widget_names[i]] = value
                    
                    new_workflow[node_id] = new_node
                
                # Copy only specific workflow metadata (skip arrays like 'links', 'groups', etc.)
                metadata_keys = ["id", "revision", "last_node_id", "last_link_id", "config", "extra", "version"]
                for key in metadata_keys:
                    if key in workflow:
                        new_workflow[key] = workflow[key]
                
                workflow = new_workflow
                logger.info(f"Converted workflow to direct node dict format with {len(workflow)} nodes")
            
            # Handle fallback for LoadImage nodes if not set by title
            if not original_image_set or not source_image_set:
                load_image_nodes = []
                # Only iterate over items that are actually nodes (dictionaries with class_type)
                # Skip non-node items like 'links', 'groups', 'config', etc.
                for node_id, node in workflow.items():
                    if (isinstance(node, dict) and 
                        node.get("class_type") == "LoadImage" and 
                        node_id not in ["links", "groups", "config", "extra", "version"]):
                        load_image_nodes.append(node_id)
                
                if len(load_image_nodes) >= 2:
                    if not original_image_set and load_image_nodes[0] in workflow:
                        workflow[load_image_nodes[0]]["inputs"]["image"] = original_filename
                        logger.info(f"Set original image in fallback node {load_image_nodes[0]}: {original_filename}")
                    if not source_image_set and len(load_image_nodes) > 1 and load_image_nodes[1] in workflow:
                        workflow[load_image_nodes[1]]["inputs"]["image"] = reference_filename
                        logger.info(f"Set reference image in fallback node {load_image_nodes[1]}: {reference_filename}")
            
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
