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
        """Prepare ComfyUI FaceDetailer workflow for face morphing"""
        try:
            # Get image filename
            import os
            import random
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