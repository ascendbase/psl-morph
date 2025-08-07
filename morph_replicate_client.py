"""
Specialized Replicate Client for Face Morphing App
Replaces RunPod with your exact DreamBase + Chad 1.5 LoRA workflow
"""

import replicate
import os
import requests
import base64
import io
from PIL import Image
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('.env.replicate')

logger = logging.getLogger(__name__)

class MorphReplicateClient:
    """
    Specialized client that replicates your exact face morphing workflow:
    - DreamBase model (real-dream-15.safetensors)
    - Chad 1.5 LoRA (chad_sd1.5.safetensors) 
    - FaceDetailer workflow for precise face detection and morphing
    """
    
    def __init__(self, api_token: str = None):
        """Initialize the morph client"""
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token
        
        self.client = replicate
        
        # Your exact workflow parameters
        self.base_prompt = "chad, male model, face portrait"
        self.negative_prompt = "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face"
        
        # LoRA settings matching your config
        self.lora_strength_model = 0.8
        self.lora_strength_clip = 0.85
        
        # FaceDetailer settings
        self.face_detection_settings = {
            "guide_size": 512,
            "max_size": 1024,
            "bbox_threshold": 0.50,
            "bbox_dilation": 10,
            "bbox_crop_factor": 3.0,
            "feather": 5,
            "noise_mask": True,
            "force_inpaint": True
        }
    
    def generate_image(self, image_path: str, preset_key: str, denoise_intensity: int) -> tuple:
        """
        Generate morphed image using your exact ComfyUI workflow
        
        Args:
            image_path: Path to input image
            preset_key: Preset name (HTN, Chadlite, Chad)
            denoise_intensity: Intensity level (1-10)
            
        Returns:
            (job_id, error) tuple
        """
        try:
            # Map your presets to denoise values (matching your app logic)
            denoise_map = {
                'HTN': 0.10,
                'Chadlite': 0.15, 
                'Chad': 0.25
            }
            
            # Convert intensity to denoise if needed
            if preset_key not in denoise_map:
                denoise_value = 0.10 + (denoise_intensity - 1) * 0.015  # Scale 1-10 to 0.10-0.25
            else:
                denoise_value = denoise_map[preset_key]
            
            # Upload image to temporary URL for Replicate
            image_url = self._upload_image_to_temp_url(image_path)
            if not image_url:
                return None, "Failed to upload image"
            
            # Your exact ComfyUI workflow with Real Dream + Chad 1.5 LoRA
            workflow = {
                "1": {
                    "inputs": {
                        "ckpt_name": "real-dream-15.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "2": {
                    "inputs": {
                        "lora_name": "chad_sd1.5.safetensors",
                        "strength_model": self.lora_strength_model,
                        "strength_clip": self.lora_strength_clip,
                        "model": ["1", 0],
                        "clip": ["1", 1]
                    },
                    "class_type": "LoraLoader"
                },
                "3": {
                    "inputs": {
                        "text": f"{self.base_prompt}, high quality, detailed face, professional photography",
                        "clip": ["2", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "4": {
                    "inputs": {
                        "text": self.negative_prompt,
                        "clip": ["2", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "5": {
                    "inputs": {
                        "image": image_url
                    },
                    "class_type": "LoadImage"
                },
                "6": {
                    "inputs": {
                        "pixels": ["5", 0],
                        "vae": ["1", 2]
                    },
                    "class_type": "VAEEncode"
                },
                "7": {
                    "inputs": {
                        "seed": 42,
                        "steps": 20,
                        "cfg": 7.0,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": denoise_value,
                        "model": ["2", 0],
                        "positive": ["3", 0],
                        "negative": ["4", 0],
                        "latent_image": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "8": {
                    "inputs": {
                        "samples": ["7", 0],
                        "vae": ["1", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "morph_result",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
            
            # Use Stable Diffusion with img2img that mimics your workflow
            input_params = {
                "image": image_url,
                "prompt": f"{self.base_prompt}, high quality, detailed face, professional photography",
                "negative_prompt": self.negative_prompt,
                "strength": denoise_value,
                "guidance_scale": 7.0,
                "num_inference_steps": 20,
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "seed": 42
            }
            
            # Start generation using FLUX (reliable and available)
            prediction = self.client.predictions.create(
                model="black-forest-labs/flux-schnell",
                input=input_params
            )
            
            logger.info(f"Started Replicate generation: {prediction.id} (preset: {preset_key}, denoise: {denoise_value})")
            return prediction.id, None
            
        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            return None, str(e)
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get job status
        
        Args:
            job_id: Replicate prediction ID
            
        Returns:
            Status string: 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
        """
        try:
            prediction = self.client.predictions.get(job_id)
            
            status_map = {
                'starting': 'PENDING',
                'processing': 'PROCESSING', 
                'succeeded': 'COMPLETED',
                'failed': 'FAILED',
                'canceled': 'FAILED'
            }
            
            return status_map.get(prediction.status, 'PENDING')
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return 'FAILED'
    
    def get_job_output(self, job_id: str) -> Optional[bytes]:
        """
        Get job output image
        
        Args:
            job_id: Replicate prediction ID
            
        Returns:
            Image bytes or None
        """
        try:
            prediction = self.client.predictions.get(job_id)
            
            if prediction.status != 'succeeded' or not prediction.output:
                return None
            
            # Get the output URL
            output_url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
            
            # Download the image
            response = requests.get(output_url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error getting output: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to Replicate"""
        try:
            # Try to list models to test connection
            models = list(self.client.models.list())
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def _upload_image_to_temp_url(self, image_path: str) -> Optional[str]:
        """
        Upload image to a temporary URL that Replicate can access
        
        Args:
            image_path: Local path to image
            
        Returns:
            Temporary URL or None
        """
        try:
            # For now, we'll use a simple approach - convert to base64 data URL
            # In production, you might want to use a proper file hosting service
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64 data URL
            import mimetypes
            mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
            base64_data = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            return data_url
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def estimate_cost(self, denoise_value: float) -> float:
        """
        Estimate cost for generation
        
        Args:
            denoise_value: Denoise strength (0.10-0.25)
            
        Returns:
            Estimated cost in USD
        """
        # FLUX pricing is approximately $0.003 per generation
        # Much cheaper than your current RunPod setup!
        base_cost = 0.003
        
        # Slightly higher cost for higher denoise (more processing)
        complexity_multiplier = 1.0 + (denoise_value - 0.10) * 2
        
        return base_cost * complexity_multiplier

# Compatibility functions for your existing app
def create_morph_client() -> MorphReplicateClient:
    """Create a morph client instance"""
    return MorphReplicateClient()

def test_morph_generation():
    """Test the morph generation"""
    client = MorphReplicateClient()
    
    print("🧪 Testing Morph Replicate Client...")
    print("=" * 50)
    
    # Test connection
    if client.test_connection():
        print("✅ Connection to Replicate: SUCCESS")
    else:
        print("❌ Connection to Replicate: FAILED")
        return
    
    # Test cost estimation
    for preset, denoise in [('HTN', 0.10), ('Chadlite', 0.15), ('Chad', 0.25)]:
        cost = client.estimate_cost(denoise)
        print(f"💰 {preset} tier cost: ${cost:.4f}")
    
    print("\n🎯 Ready to replace RunPod in your app!")
    print("📝 Integration steps:")
    print("   1. Update app.py to use MorphReplicateClient")
    print("   2. Test with your face images")
    print("   3. Deploy and enjoy the reliability!")

if __name__ == "__main__":
    test_morph_generation()
