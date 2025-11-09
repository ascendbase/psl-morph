# Docker Build Memory Error Fix
## "Bus error" Solution

## Problem

Your Docker build is failing with:
```
WARNING: Failed to remove contents in a temporary directory...
Bus error (core dumped) pip install --no-cache-dir -r requirements.txt
```

This is a **memory/disk space issue** in the Docker container during Impact Pack installation.

## Quick Fixes

### Fix 1: Add Memory Limits to Dockerfile

Add these lines to your `Dockerfile.runpod.comfyui` after the system dependencies:

```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# **ADD THIS PART:**
# Install Python dependencies with memory optimization
WORKDIR /tmp
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Set memory optimization environment variables
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=1
ENV OMP_NUM_THREADS=1
```

### Fix 2: Alternative Dockerfile (Split Installation)

Replace the current `Dockerfile.runpod.comfyui` with this optimized version:

```dockerfile
# RunPod ComfyUI with Impact Pack Pre-installed
# Optimized for low memory usage

FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to reduce memory usage
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=1
ENV OMP_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Install ComfyUI dependencies in smaller chunks
WORKDIR /app/ComfyUI

# Install basic requirements first
RUN pip install --no-cache-dir setuptools wheel

# Install PyTorch packages separately to avoid memory issues
RUN pip install --no-cache-dir -r requirements.txt --timeout 300

# Create custom nodes directory
WORKDIR /app/ComfyUI/custom_nodes

# Install Impact Pack with timeout and retry
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git || true
WORKDIR /app/ComfyUI/custom_nodes/ComfyUI-Impact-Pack

# Install with specific package versions to avoid conflicts
RUN pip install --no-cache-dir --timeout 300 \
    torch>=1.9.0 \
    torchvision>=0.10.0 \
    torchaudio>=0.9.0 \
    pillow>=8.3.0 \
    numpy>=1.21.0 \
    scipy>=1.7.0 \
    opencv-python>=4.5.0 \
    onnx>=1.10.0 \
    onnxruntime>=1.8.0

# Install remaining requirements
RUN pip install --no-cache-dir --timeout 300 -r requirements.txt || true

WORKDIR /app/ComfyUI/custom_nodes

# Install Impact Subpack
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git || true
WORKDIR /app/ComfyUI/custom_nodes/ComfyUI-Impact-Subpack
RUN pip install --no-cache-dir --timeout 300 -r requirements.txt || true

# Create model directories
WORKDIR /app/ComfyUI/models
RUN mkdir -p checkpoints loras ultralytics/bbox ultralytics/segm sams input output

# Download required models with better error handling
WORKDIR /app/ComfyUI/models

# SAM model
RUN wget --timeout=300 --tries=3 -q --show-progress -O sams/sam_vit_b_01ec64.pth \
    https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth || echo "SAM download failed, will download on first run"

# YOLO model  
RUN wget --timeout=300 --tries=3 -q --show-progress -O ultralytics/bbox/face_yolov8m.pt \
    https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt || echo "YOLO download failed, will download on first run"

# Set up API server
WORKDIR /app/ComfyUI

# Create startup script
RUN echo '#!/bin/bash\n\
PORT=${PORT:-8188}\n\
echo "Starting ComfyUI on port $PORT"\n\
python main.py --listen 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8188

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8188/ || exit 1

# Start ComfyUI
CMD ["/app/start.sh"]
```

## Alternative Solutions

### Option A: Use GitHub Actions (No Local Build)

Since local Docker build is having issues, use GitHub Actions instead:

1. **Push your code to GitHub**
2. **GitHub Actions will build automatically for free**
3. **Get the Docker image from DockerHub**

Steps:
```bash
git add .
git commit -m "Add RunPod Docker setup"
git push origin main
```

Then check the Actions tab on GitHub for build progress.

### Option B: Use Pre-built Images

Find existing ComfyUI images with Impact Pack:

1. Search DockerHub: `comfyui impact pack`
2. Use someone else's working image
3. Skip building entirely

### Option C: Build on RunPod Directly

Use RunPod's web interface to build:

1. Go to RunPod console
2. Create a new pod with ComfyUI template
3. Install Impact Pack manually
4. Save as template for serverless

## Recommended Quick Fix

**Try the alternative Dockerfile above (Fix 2)** - it splits the installation into smaller steps and adds memory optimization.

1. Replace your `Dockerfile.runpod.comfyui` with the code above
2. Run `build_and_push_comfyui.bat` again

The build will take longer but should complete without memory errors.

## Why This Happens

- Impact Pack has many large Python dependencies
- Docker containers have limited memory by default
- Pip tries to install everything at once, causing overflow
- Splitting installation prevents memory spikes

The optimized Dockerfile installs packages individually and sets memory limits.
