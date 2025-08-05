"""
RunPod Pod Client for Face Morphing App
Connects directly to a RunPod pod with ComfyUI installed
"""

import requests
import json
import time
import base64
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class RunPodPodClient:
    def __init__(self, pod_url, pod_port=8188):
        """
        Initialize RunPod Pod client for direct ComfyUI connection
        
        Args:
            pod_url: The pod's public IP or URL (e.g., "149.36.1.79:33805")
            pod_port: ComfyUI port (default 8188)
        """
        # Handle different URL formats
        if pod_url.startswith('http'):
            # Full URL provided
            self.comfyui_url = pod_url
            self.pod_ip = pod_url.split('//')[1].split(':')[0]
        elif '.proxy.runpod.net' in pod_url:
            # RunPod proxy URL - use HTTPS
            self.comfyui_url = f"https://{pod_url}"
            self.pod_ip = pod_url
        elif ':' in pod_url:
            # IP:SSH_PORT format
            ip, port = pod_url.split(':')
            self.pod_ip = ip
            self.ssh_port = port
            self.comfyui_url = f"http://{ip}:{pod_port}"
        else:
            # Just IP
            self.pod_ip = pod_url
            self.ssh_port = "22"
            self.comfyui_url = f"http://{pod_url}:{pod_port}"
        
        self.timeout = 300
        
        logger.info(f"Initialized RunPod Pod client: {self.comfyui_url}")
    
    def test_connection(self):
        """Test connection to ComfyUI on the pod"""
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats", timeout=10)
            if response.status_code == 200:
                logger.info("Successfully connected to ComfyUI on RunPod pod")
                return True
            else:
                logger.error(f"ComfyUI responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to ComfyUI on pod. Make sure ComfyUI is running on port 8188")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def generate_image(self, image_path, denoise_strength, preset_name):
        """
        Generate face morphing using ComfyUI on RunPod pod
        
        Args:
            image_path: Path to input image
            denoise_strength: Denoise strength (0.3-0.4)
            preset_name: HTN, Chadlite, or Chad
            
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
            prompt_id = self._queue_workflow(workflow)
            if prompt_id:
                logger.info(f"Started generation on RunPod pod: {prompt_id}")
                return prompt_id
            else:
                logger.error("Failed to queue workflow")
                return None
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def get_job_status(self, prompt_id):
        """Get job status from ComfyUI"""
        try:
            response = requests.get(f"{self.comfyui_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id in history:
                return "COMPLETED"
            else:
                # Check queue
                queue_response = requests.get(f"{self.comfyui_url}/queue", timeout=10)
                queue_data = queue_response.json()
                
                # Check if in running queue
                for item in queue_data.get('queue_running', []):
                    if item[1] == prompt_id:
                        return "IN_PROGRESS"
                
                # Check if in pending queue
                for item in queue_data.get('queue_pending', []):
                    if item[1] == prompt_id:
                        return "IN_QUEUE"
                
                return "FAILED"
                
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return "FAILED"
    
    def get_job_output(self, prompt_id):
        """Get job output from ComfyUI"""
        try:
            # Get history
            response = requests.get(f"{self.comfyui_url}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            
            history = response.json()
            if prompt_id not in history:
                logger.error("Job not found in history")
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
                        
                        img_response = requests.get(f"{self.comfyui_url}/view", params=params, timeout=30)
                        img_response.raise_for_status()
                        
                        return img_response.content
            
            logger.error("No output images found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job output: {e}")
            return None
    
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
    
    def _queue_workflow(self, workflow):
        """Queue workflow in ComfyUI"""
        try:
            import uuid
            prompt_id = str(uuid.uuid4())
            
            payload = {
                "prompt": workflow,
                "client_id": prompt_id
            }
            
            response = requests.post(
                f"{self.comfyui_url}/prompt",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('prompt_id', prompt_id)
            
        except Exception as e:
            logger.error(f"Failed to queue workflow: {e}")
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
                response = requests.post(f"{self.comfyui_url}/upload/image", files=files, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Uploaded image to ComfyUI: {filename} -> {result}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return False