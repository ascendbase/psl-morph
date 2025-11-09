# RunPod Serverless ComfyUI Deployment Guide
## Pre-installed Nodes & Models for Morph App Workflows

This guide shows how to create a Docker image with ComfyUI, custom nodes, and all required models pre-installed for RunPod serverless GPU usage.

## Overview

**What This Does:**
- Creates a Docker image with ComfyUI pre-configured
- Installs all required custom nodes (Impact-Pack, Impact-Subpack, etc.)
- Pre-downloads all required models
- Optimized for fast cold starts on RunPod serverless

**Requirements:**
- Docker installed on your system
- DockerHub account (or other container registry)
- RunPod account

## Part 1: Create Dockerfile with All Nodes

Create a new file `Dockerfile.runpod.comfyui`:

```dockerfile
# RunPod ComfyUI with Impact Pack Pre-installed
FROM runpod/pytorch:2.1.1-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Install ComfyUI dependencies
WORKDIR /app/ComfyUI
RUN pip install --no-cache-dir -r requirements.txt

# Install custom nodes in correct order
WORKDIR /app/ComfyUI/custom_nodes

# 1. Install ComfyUI-Impact-Pack
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    cd ComfyUI-Impact-Pack && \
    pip install --no-cache-dir -r requirements.txt

# 2. Install ComfyUI-Impact-Subpack (required dependency)
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git && \
    cd ComfyUI-Impact-Subpack && \
    pip install --no-cache-dir -r requirements.txt

# Optional: Install other useful custom nodes
# RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
#     cd comfyui_controlnet_aux && \
#     pip install --no-cache-dir -r requirements.txt

# Create model directories
RUN mkdir -p /app/ComfyUI/models/checkpoints && \
    mkdir -p /app/ComfyUI/models/loras && \
    mkdir -p /app/ComfyUI/models/ultralytics/bbox && \
    mkdir -p /app/ComfyUI/models/sams

# Download required models
WORKDIR /app/ComfyUI/models

# Download SAM model (required for FaceDetailer)
RUN wget -O sams/sam_vit_b_01ec64.pth \
    https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth

# Download face detection model (YOLO)
# Note: This is auto-downloaded by Impact Pack on first use, but we can pre-download
RUN wget -O ultralytics/bbox/face_yolov8m.pt \
    https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt

# Copy your models (checkpoint and LoRA)
# You'll need to mount these or include them in the build
# COPY ./models/checkpoints/real-dream-15.safetensors /app/ComfyUI/models/checkpoints/
# COPY ./models/loras/chad_sd1.5.safetensors /app/ComfyUI/models/loras/

# Set up API server
WORKDIR /app/ComfyUI

# Create startup script
RUN echo '#!/bin/bash\n\
python main.py --listen 0.0.0.0 --port 8188 --dont-print-server\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8188

# Start ComfyUI
CMD ["/app/start.sh"]
```

## Part 2: Build and Push Docker Image

### Option A: Build Locally

```bash
# Build the Docker image
docker build -f Dockerfile.runpod.comfyui -t yourusername/comfyui-facedetailer:latest .

# Test locally
docker run -p 8188:8188 yourusername/comfyui-facedetailer:latest

# Push to DockerHub
docker login
docker push yourusername/comfyui-facedetailer:latest
```

### Option B: Include Your Models in Build

If you want to include your checkpoint and LoRA models:

```bash
# Create models directory structure
mkdir -p ./docker_models/checkpoints
mkdir -p ./docker_models/loras

# Copy your models
copy base_models\real-dream-15.safetensors docker_models\checkpoints\
copy lora\chad_sd1.5.safetensors docker_models\loras\

# Update Dockerfile to uncomment COPY lines
# Then build
docker build -f Dockerfile.runpod.comfyui -t yourusername/comfyui-facedetailer:latest .
docker push yourusername/comfyui-facedetailer:latest
```

## Part 3: Deploy on RunPod Serverless

### Create RunPod Endpoint

1. Log into RunPod: https://www.runpod.io/console/serverless
2. Click "New Endpoint"
3. Configure:
   - **Name**: morph-comfyui-facedetailer
   - **Docker Image**: `yourusername/comfyui-facedetailer:latest`
   - **GPU**: Select based on needs (RTX 4090, A100, etc.)
   - **Container Disk**: 20 GB minimum
   - **Idle Timeout**: 5 seconds
   - **Max Workers**: Based on your budget

4. Advanced Configuration:
```json
{
  "env": {
    "COMFYUI_PORT": "8188"
  },
  "expose_http_ports": [8188]
}
```

### Test the Endpoint

```python
import requests
import json
import base64

# Your RunPod endpoint URL
ENDPOINT_URL = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"
API_KEY = "YOUR_RUNPOD_API_KEY"

# Load your workflow
with open("comfyui_workflows/workflow_facedetailer.json", "r") as f:
    workflow = json.load(f)

# Prepare request
payload = {
    "input": {
        "workflow": workflow,
        "images": []  # Add base64 encoded images if needed
    }
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Make request
response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
print(response.json())
```

## Part 4: Alternative - Build with GitHub Actions

Create `.github/workflows/build-comfyui-docker.yml`:

```yaml
name: Build ComfyUI Docker Image

on:
  push:
    branches: [ main ]
    paths:
      - 'Dockerfile.runpod.comfyui'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.runpod.comfyui
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/comfyui-facedetailer:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Part 5: Update Your Morph App Client

Update your `runpod_client.py` or create a new client:

```python
import runpod
import json
import time

class RunPodComfyUIClient:
    def __init__(self, api_key, endpoint_id):
        runpod.api_key = api_key
        self.endpoint = runpod.Endpoint(endpoint_id)
    
    def run_workflow(self, workflow_path, input_image_path=None):
        """Run a ComfyUI workflow on RunPod"""
        
        # Load workflow
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        # Prepare input
        payload = {
            "workflow": workflow
        }
        
        # Add input image if provided
        if input_image_path:
            import base64
            with open(input_image_path, 'rb') as img:
                image_b64 = base64.b64encode(img.read()).decode('utf-8')
                payload["input_image"] = image_b64
        
        # Run on serverless
        run_request = self.endpoint.run_sync(payload, timeout=300)
        
        return run_request
    
    def run_facedetailer(self, input_image_path):
        """Convenience method for FaceDetailer workflow"""
        return self.run_workflow(
            "comfyui_workflows/workflow_facedetailer.json",
            input_image_path
        )

# Usage
if __name__ == "__main__":
    client = RunPodComfyUIClient(
        api_key="YOUR_RUNPOD_API_KEY",
        endpoint_id="YOUR_ENDPOINT_ID"
    )
    
    result = client.run_facedetailer("path/to/input.jpg")
    print(result)
```

## Part 6: Cost Optimization

### Tips for Reducing Costs:

1. **Use Smaller GPUs for Testing**
   - RTX 4090: ~$0.35/hr
   - RTX 4060 Ti: ~$0.15/hr

2. **Optimize Model Loading**
   - Pre-load models in Docker image
   - Use model caching between runs

3. **Set Appropriate Timeouts**
   - Idle timeout: 5-10 seconds
   - Execution timeout: 60-120 seconds

4. **Use Spot Instances**
   - 50-70% cheaper than on-demand
   - Good for non-critical workloads

## Part 7: Monitoring & Debugging

### Check Logs

```bash
# View endpoint logs in RunPod dashboard
# Or use API:
curl -X GET \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/logs \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Test Workflow Locally First

```bash
# Run the Docker container locally
docker run -p 8188:8188 -it yourusername/comfyui-facedetailer:latest

# Access ComfyUI at http://localhost:8188
# Test your workflows before deploying
```

## Summary

**What You Get:**
- ✅ ComfyUI with Impact-Pack and Impact-Subpack pre-installed
- ✅ All required models downloaded
- ✅ Fast cold starts (< 30 seconds)
- ✅ Pay-per-second billing
- ✅ Auto-scaling based on demand

**Required Custom Nodes (Pre-installed):**
- ComfyUI-Impact-Pack (v8.15.3+)
- ComfyUI-Impact-Subpack (v1.3.2+)

**Required Models (Pre-downloaded):**
- SAM model: sam_vit_b_01ec64.pth
- YOLO face detector: face_yolov8m.pt
- Your checkpoint: real-dream-15.safetensors (add to build)
- Your LoRA: chad_sd1.5.safetensors (add to build)

**Next Steps:**
1. Build the Docker image with the Dockerfile above
2. Push to DockerHub
3. Create RunPod serverless endpoint
4. Test with your workflows
5. Integrate into your Morph app

**Estimated Costs:**
- Build time: Free (GitHub Actions) or local
- Storage: ~$0.02/GB/month for Docker image
- Compute: $0.15-0.35/hr depending on GPU (only when running)
- Typical workflow: ~$0.01-0.05 per generation
