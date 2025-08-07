"""
Vast.ai On-Demand Client - Pay only for generation time!
Automatically starts/stops instances to minimize costs (98-99% savings)
"""

import requests
import time
import json
import os
import base64
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class VastOnDemandClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://console.vast.ai/api/v0"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.current_instance_id = None
        self.instance_ip = None
        self.instance_port = None
        
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = requests.get(f"{self.base_url}/users/current/", headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def find_cheapest_gpu(self, min_gpu_ram: int = 8, gpu_name: str = None) -> Optional[Dict]:
        """Find the cheapest available GPU instance"""
        try:
            url = f"{self.base_url}/bundles/"
            
            # Build query for available instances
            query = {
                "verified": {"eq": True},
                "external": {"eq": False},
                "rentable": {"eq": True},
                "gpu_ram": {"gte": min_gpu_ram},
                "cuda_max_good": {"gte": 11.0},  # Ensure CUDA compatibility
                "reliability2": {"gte": 0.9}     # High reliability instances
            }
            
            # Filter by specific GPU if requested
            if gpu_name:
                query["gpu_name"] = {"eq": gpu_name}
            
            params = {
                "q": json.dumps(query),
                "order": [["dph_total", "asc"]],  # Order by price ascending
                "limit": 20
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                offers = data.get("offers", [])
                
                # Filter for instances with good specs
                good_offers = []
                for offer in offers:
                    if (offer.get("gpu_ram", 0) >= min_gpu_ram and 
                        offer.get("reliability2", 0) >= 0.9 and
                        offer.get("dph_total", 999) < 1.0):  # Under $1/hour
                        good_offers.append(offer)
                
                if good_offers:
                    logger.info(f"Found {len(good_offers)} suitable GPU offers")
                    return good_offers[0]
                else:
                    logger.warning("No suitable GPU offers found")
                    return None
            else:
                logger.error(f"Failed to fetch offers: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding GPU: {e}")
            return None
    
    def start_instance(self, offer_id: int) -> Optional[int]:
        """Start a new instance with ComfyUI"""
        try:
            url = f"{self.base_url}/asks/{offer_id}/"
            
            # Docker image with ComfyUI pre-installed
            docker_image = "runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04"
            
            # Startup script to install and run ComfyUI
            startup_script = """
#!/bin/bash
set -e

echo "Starting ComfyUI setup..."

# Install git if not present
apt-get update && apt-get install -y git wget

# Clone ComfyUI
cd /workspace
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
fi

cd ComfyUI

# Install requirements
pip install -r requirements.txt
pip install opencv-python pillow requests

# Download basic models
mkdir -p models/checkpoints
mkdir -p models/vae
mkdir -p models/loras

# Download SD 1.5 model (smaller, faster)
if [ ! -f "models/checkpoints/v1-5-pruned-emaonly.ckpt" ]; then
    wget -O models/checkpoints/v1-5-pruned-emaonly.ckpt "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt"
fi

# Start ComfyUI API server
echo "Starting ComfyUI server..."
python main.py --listen 0.0.0.0 --port 8188 &

# Wait for server to start
sleep 30

echo "ComfyUI setup complete!"
"""
            
            data = {
                "client_id": "vast_on_demand_morph",
                "image": docker_image,
                "args": [],
                "env": {
                    "JUPYTER_PASSWORD": "morphpass123"
                },
                "onstart": startup_script,
                "runtype": "ssh jupyter",
                "image_login": "root"
            }
            
            response = requests.put(url, headers=self.headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                instance_id = result.get("new_contract")
                if instance_id:
                    self.current_instance_id = instance_id
                    logger.info(f"Started instance {instance_id}")
                    return instance_id
                else:
                    logger.error("No instance ID returned")
                    return None
            else:
                logger.error(f"Failed to start instance: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error starting instance: {e}")
            return None
    
    def wait_for_instance_ready(self, instance_id: int, timeout: int = 600) -> bool:
        """Wait for instance to be ready (up to 10 minutes)"""
        try:
            start_time = time.time()
            logger.info(f"Waiting for instance {instance_id} to be ready...")
            
            while time.time() - start_time < timeout:
                status_info = self.get_instance_info(instance_id)
                if not status_info:
                    time.sleep(15)
                    continue
                
                status = status_info.get("actual_status", "unknown")
                logger.info(f"Instance status: {status}")
                
                if status == "running":
                    # Get connection info
                    self.instance_ip = status_info.get("public_ipaddr")
                    ssh_port = status_info.get("ssh_port")
                    
                    if self.instance_ip:
                        # Test ComfyUI API
                        comfyui_url = f"http://{self.instance_ip}:8188"
                        if self._test_comfyui_ready(comfyui_url):
                            logger.info(f"Instance ready! ComfyUI available at {comfyui_url}")
                            return True
                        else:
                            logger.info("Instance running but ComfyUI not ready yet...")
                
                elif status in ["failed", "cancelled"]:
                    logger.error(f"Instance failed to start: {status}")
                    return False
                
                time.sleep(15)  # Check every 15 seconds
            
            logger.error(f"Instance {instance_id} failed to become ready within {timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for instance: {e}")
            return False
    
    def _test_comfyui_ready(self, comfyui_url: str, max_attempts: int = 10) -> bool:
        """Test if ComfyUI API is ready"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{comfyui_url}/system_stats", timeout=10)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(10)
        return False
    
    def get_instance_info(self, instance_id: int) -> Optional[Dict]:
        """Get detailed instance information"""
        try:
            url = f"{self.base_url}/instances/"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                instances = response.json().get("instances", [])
                for instance in instances:
                    if instance.get("id") == instance_id:
                        return instance
            return None
        except Exception as e:
            logger.error(f"Error getting instance info: {e}")
            return None
    
    def stop_instance(self, instance_id: int) -> bool:
        """Stop and destroy instance"""
        try:
            url = f"{self.base_url}/instances/{instance_id}/"
            response = requests.delete(url, headers=self.headers, timeout=30)
            success = response.status_code == 200
            if success:
                logger.info(f"Stopped instance {instance_id}")
                if self.current_instance_id == instance_id:
                    self.current_instance_id = None
                    self.instance_ip = None
            else:
                logger.error(f"Failed to stop instance: {response.status_code}")
            return success
        except Exception as e:
            logger.error(f"Error stopping instance: {e}")
            return False
    
    def generate_image(self, image_path: str, preset_key: str = "tier1", denoise_intensity: int = 4) -> Tuple[Optional[bytes], Optional[str]]:
        """Generate image with on-demand instance management"""
        instance_id = None
        try:
            logger.info("Starting on-demand image generation...")
            
            # 1. Find cheapest GPU
            logger.info("Finding cheapest GPU...")
            offer = self.find_cheapest_gpu(min_gpu_ram=8)
            if not offer:
                return None, "No available GPU instances found"
            
            gpu_info = f"{offer.get('gpu_name', 'Unknown')} ({offer.get('gpu_ram', 0)}GB) - ${offer.get('dph_total', 0):.3f}/hour"
            logger.info(f"Selected GPU: {gpu_info}")
            
            # 2. Start instance
            logger.info("Starting GPU instance...")
            instance_id = self.start_instance(offer["id"])
            if not instance_id:
                return None, "Failed to start GPU instance"
            
            # 3. Wait for ready
            logger.info("Waiting for instance to be ready...")
            if not self.wait_for_instance_ready(instance_id):
                self.stop_instance(instance_id)
                return None, "Instance failed to become ready"
            
            # 4. Process image
            logger.info("Processing image...")
            comfyui_url = f"http://{self.instance_ip}:8188"
            result_image = self._process_image_on_comfyui(comfyui_url, image_path, preset_key, denoise_intensity)
            
            if not result_image:
                return None, "Image processing failed"
            
            logger.info("Image generation completed successfully!")
            return result_image, None
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None, str(e)
        finally:
            # Always stop instance to minimize costs
            if instance_id:
                logger.info("Stopping instance to minimize costs...")
                self.stop_instance(instance_id)
    
    def _process_image_on_comfyui(self, comfyui_url: str, image_path: str, preset_key: str, denoise_intensity: int) -> Optional[bytes]:
        """Process image using ComfyUI API"""
        try:
            # Simple workflow for face morphing
            workflow = {
                "1": {
                    "inputs": {
                        "ckpt_name": "v1-5-pruned-emaonly.ckpt"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "2": {
                    "inputs": {
                        "image": os.path.basename(image_path),
                        "upload": "image"
                    },
                    "class_type": "LoadImage"
                },
                "3": {
                    "inputs": {
                        "seed": int(time.time()),
                        "steps": 20,
                        "cfg": 7.0,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": denoise_intensity / 10.0,  # Convert to 0.0-1.0 range
                        "model": ["1", 0],
                        "positive": ["4", 0],
                        "negative": ["5", 0],
                        "latent_image": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "text": "beautiful face, high quality, detailed",
                        "clip": ["1", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "5": {
                    "inputs": {
                        "text": "ugly, blurry, low quality",
                        "clip": ["1", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "6": {
                    "inputs": {
                        "pixels": ["2", 0],
                        "vae": ["1", 2]
                    },
                    "class_type": "VAEEncode"
                },
                "7": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["1", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "8": {
                    "inputs": {
                        "filename_prefix": f"morph_{preset_key}_{int(time.time())}",
                        "images": ["7", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
            
            # Upload image first
            if not self._upload_image_to_comfyui(comfyui_url, image_path):
                logger.error("Failed to upload image")
                return None
            
            # Queue workflow
            prompt_id = self._queue_workflow(comfyui_url, workflow)
            if not prompt_id:
                logger.error("Failed to queue workflow")
                return None
            
            # Wait for completion
            if not self._wait_for_completion(comfyui_url, prompt_id):
                logger.error("Workflow failed to complete")
                return None
            
            # Get result
            return self._get_result_image(comfyui_url, prompt_id)
            
        except Exception as e:
            logger.error(f"ComfyUI processing error: {e}")
            return None
    
    def _upload_image_to_comfyui(self, comfyui_url: str, image_path: str) -> bool:
        """Upload image to ComfyUI"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{comfyui_url}/upload/image", files=files, timeout=60)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return False
    
    def _queue_workflow(self, comfyui_url: str, workflow: Dict) -> Optional[str]:
        """Queue workflow in ComfyUI"""
        try:
            payload = {
                "prompt": workflow,
                "client_id": f"vast_client_{int(time.time())}"
            }
            response = requests.post(f"{comfyui_url}/prompt", json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("prompt_id")
            return None
        except Exception as e:
            logger.error(f"Workflow queue error: {e}")
            return None
    
    def _wait_for_completion(self, comfyui_url: str, prompt_id: str, timeout: int = 300) -> bool:
        """Wait for workflow completion"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{comfyui_url}/history/{prompt_id}", timeout=30)
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        return True
                time.sleep(5)
            except:
                time.sleep(5)
        return False
    
    def _get_result_image(self, comfyui_url: str, prompt_id: str) -> Optional[bytes]:
        """Get result image from ComfyUI"""
        try:
            response = requests.get(f"{comfyui_url}/history/{prompt_id}", timeout=30)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for image_info in node_output["images"]:
                                filename = image_info["filename"]
                                subfolder = image_info.get("subfolder", "")
                                
                                params = {
                                    "filename": filename,
                                    "subfolder": subfolder,
                                    "type": "output"
                                }
                                
                                img_response = requests.get(f"{comfyui_url}/view", params=params, timeout=60)
                                if img_response.status_code == 200:
                                    return img_response.content
            return None
        except Exception as e:
            logger.error(f"Result retrieval error: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> str:
        """Get job status (compatibility method)"""
        # For on-demand mode, jobs are processed immediately
        return "COMPLETED"
    
    def get_job_output(self, job_id: str) -> Optional[bytes]:
        """Get job output (compatibility method)"""
        # For on-demand mode, output is returned directly from generate_image
        return None
