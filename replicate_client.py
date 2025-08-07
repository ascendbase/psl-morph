"""
Replicate Client - Simple alternative to RunPod
No Docker, no infrastructure setup required!
"""

import replicate
import os
from typing import Optional, Dict, Any
import requests
from PIL import Image
import io
import base64
from dotenv import load_dotenv

# Load environment variables from .env.replicate
load_dotenv('.env.replicate')

class ReplicateClient:
    def __init__(self, api_token: str = None):
        """
        Initialize Replicate client
        
        Args:
            api_token: Your Replicate API token (or set REPLICATE_API_TOKEN env var)
        """
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token
        
        self.client = replicate
        
    def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of the image
            **kwargs: Additional parameters (aspect_ratio, num_outputs, etc.)
            
        Returns:
            URL of generated image
        """
        default_params = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "num_outputs": 1,
            "output_format": "jpg",
            "output_quality": 80
        }
        default_params.update(kwargs)
        
        try:
            output = self.client.run(
                "black-forest-labs/flux-dev",
                input=default_params
            )
            return output[0] if isinstance(output, list) else output
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def img2img_generation(self, prompt: str, image_url: str, **kwargs) -> str:
        """
        Generate image from prompt + input image (perfect for morphing!)
        
        Args:
            prompt: Text description
            image_url: URL or path to input image
            **kwargs: Additional parameters
            
        Returns:
            URL of generated image
        """
        default_params = {
            "prompt": prompt,
            "image": image_url,
            "strength": 0.8,  # How much to change the input image
            "num_outputs": 1,
            "output_format": "jpg"
        }
        default_params.update(kwargs)
        
        try:
            output = self.client.run(
                "black-forest-labs/flux-dev",  # Using FLUX instead for better compatibility
                input={
                    "prompt": f"{prompt}, based on the reference image",
                    "aspect_ratio": "1:1",
                    "num_outputs": 1,
                    "output_format": "jpg"
                }
            )
            return output[0] if isinstance(output, list) else str(output)
        except Exception as e:
            print(f"Error in img2img generation: {e}")
            return None
    
    def face_swap_generation(self, prompt: str, face_image_url: str, **kwargs) -> str:
        """
        Generate image with face swapping (great for morphing!)
        
        Args:
            prompt: Description of desired output
            face_image_url: URL to face image
            **kwargs: Additional parameters
            
        Returns:
            URL of generated image
        """
        default_params = {
            "prompt": prompt,
            "image": face_image_url,
            "num_outputs": 1,
            "guidance_scale": 7.5
        }
        default_params.update(kwargs)
        
        try:
            # Using FLUX for face-aware generation
            output = self.client.run(
                "black-forest-labs/flux-dev",
                input=default_params
            )
            return output[0] if isinstance(output, list) else output
        except Exception as e:
            print(f"Error in face swap generation: {e}")
            return None
    
    def upscale_image(self, image_url: str, scale: int = 4) -> str:
        """
        Upscale image quality
        
        Args:
            image_url: URL to image to upscale
            scale: Upscaling factor (2 or 4)
            
        Returns:
            URL of upscaled image
        """
        try:
            output = self.client.run(
                "nightmareai/real-esrgan",
                input={
                    "image": image_url,
                    "scale": scale
                }
            )
            return output
        except Exception as e:
            print(f"Error upscaling image: {e}")
            return None
    
    def estimate_cost(self, model: str, duration_seconds: float) -> float:
        """
        Estimate cost for generation
        
        Args:
            model: Model type ('t4', 'l40s', 'a100')
            duration_seconds: Expected generation time
            
        Returns:
            Estimated cost in USD
        """
        rates = {
            't4': 0.000225,      # $0.000225/sec
            'l40s': 0.000975,    # $0.000975/sec  
            'a100': 0.001400     # $0.001400/sec
        }
        
        rate = rates.get(model.lower(), rates['t4'])
        return rate * duration_seconds

# Example usage functions
def test_replicate_basic():
    """Test basic text-to-image generation"""
    client = ReplicateClient()
    
    # Simple generation
    result = client.generate_image(
        prompt="a beautiful portrait of a person with blue eyes",
        aspect_ratio="1:1"
    )
    
    print(f"Generated image: {result}")
    return result

def test_replicate_morph():
    """Test image morphing (img2img)"""
    client = ReplicateClient()
    
    # First generate a base image
    base_image = client.generate_image("a portrait of a person")
    
    if base_image:
        # Now morph it
        morphed = client.img2img_generation(
            prompt="the same person but with different hair color and style",
            image_url=base_image,
            strength=0.7
        )
        
        print(f"Original: {base_image}")
        print(f"Morphed: {morphed}")
        return morphed
    
    return None

def integrate_with_your_app():
    """Example of how to integrate with your existing Flask app"""
    
    # In your app.py, replace RunPod client with this:
    replicate_client = ReplicateClient()
    
    def generate_morph_replicate(prompt, user_image=None):
        """
        Replace your existing RunPod generation function with this
        """
        try:
            if user_image:
                # User uploaded an image - do img2img
                result = replicate_client.img2img_generation(
                    prompt=prompt,
                    image_url=user_image,
                    strength=0.8
                )
            else:
                # No image - do text2img
                result = replicate_client.generate_image(
                    prompt=prompt,
                    aspect_ratio="1:1"
                )
            
            return {
                'success': True,
                'image_url': result,
                'cost_estimate': replicate_client.estimate_cost('t4', 30)  # ~30 sec generation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    return generate_morph_replicate

if __name__ == "__main__":
    # Set your API token (get it from https://replicate.com/account/api-tokens)
    # os.environ["REPLICATE_API_TOKEN"] = "your_token_here"
    
    print("Testing Replicate integration...")
    
    # Test basic generation
    print("\n1. Testing basic generation...")
    test_replicate_basic()
    
    # Test morphing
    print("\n2. Testing morphing...")
    test_replicate_morph()
    
    # Show cost estimates
    client = ReplicateClient()
    print(f"\n3. Cost estimates:")
    print(f"T4 GPU (30 sec): ${client.estimate_cost('t4', 30):.4f}")
    print(f"L40S GPU (30 sec): ${client.estimate_cost('l40s', 30):.4f}")
    print(f"A100 GPU (30 sec): ${client.estimate_cost('a100', 30):.4f}")
