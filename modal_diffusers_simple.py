"""
Simplified Modal.com implementation for face morphing using Diffusers
"""

import modal
import os
import base64
import io
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DDIMScheduler
from safetensors.torch import load_file

# Create Modal app
app = modal.App("face-morph-diffusers")

# Create persistent volume for models
models_volume = modal.Volume.from_name("face-models", create_if_missing=True)

# Define the Diffusers image
diffusers_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "torch==2.0.1",
        "torchvision==0.15.2",
        "diffusers==0.18.2",
        "accelerate==0.20.3",
        "safetensors==0.3.1",
        "transformers>=4.38.1",
        "xformers==0.0.20",
        "pillow==10.0.0"
    ])
)

@app.function(
    image=diffusers_image,
    volumes={"/models": models_volume},
    gpu="T4",
    timeout=600,
    memory=16384,
    cpu=4
)
def generate_with_diffusers(image_b64: str, preset_key: str, denoise_strength: float = 0.15):
    """
    Generate face morph using Diffusers with SD 1.5 and LoRA
    """
    try:
        # Load the base model
        model_path = "/models/base_models/realdream_v12.safetensors"
        pipe = StableDiffusionImg2ImgPipeline.from_single_file(model_path, torch_dtype=torch.float16, use_safetensors=True)
        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to("cuda")

        # Load and apply the LoRA
        lora_path = "/models/lora/chad_sd1.5.safetensors"
        state_dict = load_file(lora_path)
        pipe.load_lora_weights(state_dict)
        pipe.fuse_lora()

        # Prepare the input image
        image_data = base64.b64decode(image_b64)
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")

        # Generate the image
        prompt = f"face morph, {preset_key}, high quality, detailed, realistic"
        negative_prompt = "blurry, low quality, distorted, deformed, ugly"
        
        generator = torch.Generator("cuda").manual_seed(torch.randint(0, 1000000, (1,)).item())

        output_image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=input_image,
            strength=denoise_strength,
            guidance_scale=7.5,
            num_inference_steps=25,
            generator=generator
        ).images[0]

        # Convert to base64
        buffered = io.BytesIO()
        output_image.save(buffered, format="PNG")
        result_b64 = base64.b64encode(buffered.getvalue()).decode()

        return result_b64, None

    except Exception as e:
        return None, str(e)
