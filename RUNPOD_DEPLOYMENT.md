# RunPod Cloud GPU Deployment Guide

## Overview

RunPod provides the most cost-effective solution for hosting ComfyUI with GPU acceleration. This guide covers both serverless and pod-based deployment options.

## Option 1: RunPod Serverless (Recommended)

### Advantages
- **Pay-per-second billing** - Only pay when processing
- **Auto-scaling** - Handles traffic spikes automatically
- **No idle costs** - Zero cost when not in use
- **Built-in templates** - Pre-configured ComfyUI environments

### Setup Steps

1. **Create RunPod Account**
   - Sign up at https://runpod.io
   - Add payment method
   - Get API key from Settings

2. **Deploy ComfyUI Template**
   ```bash
   # Use RunPod's official ComfyUI template
   Template ID: runpod/comfyui:latest
   ```

3. **Configure Environment Variables**
   ```bash
   COMFYUI_FLAGS=--listen 0.0.0.0 --port 8188 --api-only
   INSTALL_EXTENSIONS=true
   ```

4. **Install Required Extensions**
   - ComfyUI-Impact-Pack (FaceDetailer)
   - ComfyUI_UltralyticsDetectorProvider
   - ComfyUI_Segment_Anything

### API Integration

Update your Flask app configuration:

```python
# config.py
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY', '')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', '')
USE_CLOUD_GPU = True

# ComfyUI will be accessed via RunPod's endpoint
COMFYUI_URL = f'https://{RUNPOD_ENDPOINT_ID}-8188.proxy.runpod.net'
```

## Option 2: RunPod Pods (Always-On)

### When to Use
- High traffic (>100 generations/day)
- Need instant response (no cold start)
- Predictable usage patterns

### Setup Steps

1. **Create Pod**
   - Choose RTX 4090 or A100
   - Select ComfyUI template
   - Configure storage (20GB minimum)

2. **Install Models**
   ```bash
   # SSH into pod and install models
   cd /workspace/ComfyUI/models/checkpoints
   wget https://your-model-url/real-dream-15.safetensors
   
   cd /workspace/ComfyUI/models/loras
   wget https://your-model-url/chad_sd1.5.safetensors
   ```

3. **Configure Networking**
   - Expose port 8188
   - Enable HTTP access
   - Note the pod URL

## Cost Comparison

### Serverless Pricing (RTX 4090)
- **Idle**: $0.00/hour
- **Active**: $0.39/hour
- **Per generation**: ~$0.003 (30 seconds avg)
- **1000 generations/month**: ~$3.00

### Pod Pricing (RTX 4090)
- **24/7 operation**: $0.34/hour = $244.80/month
- **8 hours/day**: $81.60/month
- **Break-even**: ~27,000 generations/month

## Deployment Configuration Files

### 1. RunPod Serverless Handler

```python
# runpod_handler.py
import runpod
import requests
import json
import base64
from io import BytesIO
from PIL import Image

def handler(event):
    """RunPod serverless handler for ComfyUI workflow"""
    
    # Extract workflow and image from event
    workflow = event['input']['workflow']
    image_data = event['input']['image_data']
    
    # Process with local ComfyUI instance
    try:
        # Queue workflow
        response = requests.post(
            'http://127.0.0.1:8188/prompt',
            json={'prompt': workflow, 'client_id': 'runpod'},
            timeout=300
        )
        
        if response.status_code != 200:
            return {'error': f'Failed to queue workflow: {response.text}'}
        
        prompt_id = response.json()['prompt_id']
        
        # Wait for completion and get result
        result_image = wait_for_completion(prompt_id)
        
        if result_image:
            # Convert to base64 for return
            buffered = BytesIO()
            result_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                'status': 'success',
                'image': img_str,
                'prompt_id': prompt_id
            }
        else:
            return {'error': 'Failed to generate image'}
            
    except Exception as e:
        return {'error': str(e)}

def wait_for_completion(prompt_id, timeout=300):
    """Wait for ComfyUI to complete processing"""
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://127.0.0.1:8188/history/{prompt_id}')
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    # Get output image
                    return get_output_image(prompt_id, history[prompt_id])
        except:
            pass
        
        time.sleep(2)
    
    return None

def get_output_image(prompt_id, history_data):
    """Extract output image from ComfyUI history"""
    try:
        outputs = history_data.get('outputs', {})
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for image_info in node_output['images']:
                    filename = image_info['filename']
                    
                    response = requests.get(
                        f'http://127.0.0.1:8188/view',
                        params={'filename': filename, 'type': 'output'}
                    )
                    
                    if response.status_code == 200:
                        return Image.open(BytesIO(response.content))
        return None
    except:
        return None

# Start the RunPod serverless worker
runpod.serverless.start({"handler": handler})
```

### 2. Docker Configuration

```dockerfile
# Dockerfile.runpod
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /workspace

# Install ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /workspace/ComfyUI

# Install requirements
RUN pip install -r requirements.txt
RUN pip install runpod

# Install extensions
RUN cd custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    git clone https://github.com/MrForExample/ComfyUI-3D-Pack.git && \
    git clone https://github.com/storyicon/comfyui_segment_anything.git

# Copy models (you'll need to provide these)
COPY models/checkpoints/real-dream-15.safetensors models/checkpoints/
COPY models/loras/chad_sd1.5.safetensors models/loras/

# Copy handler
COPY runpod_handler.py .

# Start ComfyUI and handler
CMD python main.py --listen 0.0.0.0 --port 8188 --api-only & python runpod_handler.py
```

### 3. Environment Variables

```bash
# .env for RunPod deployment
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
USE_CLOUD_GPU=true
COMFYUI_URL=https://your-endpoint-8188.proxy.runpod.net
```

## Integration with Flask App

### Update ComfyUI Client

```python
# cloud_gpu.py
import requests
import os
from config import RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID, USE_CLOUD_GPU

class CloudGPUClient:
    def __init__(self):
        self.api_key = RUNPOD_API_KEY
        self.endpoint_id = RUNPOD_ENDPOINT_ID
        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
    
    def queue_workflow(self, workflow, image_data):
        """Queue workflow on RunPod serverless"""
        
        payload = {
            "input": {
                "workflow": workflow,
                "image_data": image_data
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/run",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()['id'], None
        else:
            return None, f"RunPod error: {response.text}"
    
    def check_status(self, job_id):
        """Check job status on RunPod"""
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['status'], data.get('output')
        else:
            return 'FAILED', None
```

## Monitoring and Scaling

### Cost Monitoring
- Set up RunPod spending alerts
- Monitor usage patterns
- Optimize based on peak hours

### Performance Optimization
- Use image compression for uploads
- Implement result caching
- Batch multiple requests when possible

### Scaling Strategy
1. **Start with Serverless** for initial launch
2. **Monitor usage patterns** for 1-2 months
3. **Switch to Pods** if usage exceeds break-even point
4. **Hybrid approach** for peak hours

## Next Steps

1. **Set up RunPod account** and get API credentials
2. **Deploy ComfyUI template** with required extensions
3. **Test workflow execution** with sample images
4. **Update Flask app** to use cloud GPU client
5. **Monitor costs and performance** after deployment

This setup provides a scalable, cost-effective solution for your Kyrgyzstan-based face morphing service with global reach.