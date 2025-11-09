# RunPod ComfyUI Quick Start Guide
## Get Your Morph App Running on RunPod in 30 Minutes

This guide will walk you through deploying ComfyUI with all required nodes to RunPod serverless.

## Prerequisites

✅ **Docker Desktop** installed and running
✅ **DockerHub account** (free) - https://hub.docker.com/signup
✅ **RunPod account** (free tier available) - https://www.runpod.io/console/signup
✅ **Your checkpoint and LoRA models** ready

## Step 1: Prepare Your Models (Optional)

If you want to include your models in the Docker image:

```bash
# Create directory structure
mkdir docker_models
mkdir docker_models\checkpoints
mkdir docker_models\loras

# Copy your models
copy base_models\real-dream-15.safetensors docker_models\checkpoints\
copy lora\chad_sd1.5.safetensors docker_models\loras\
```

Then edit `Dockerfile.runpod.comfyui` and uncomment these lines:
```dockerfile
COPY docker_models/checkpoints/real-dream-15.safetensors /app/ComfyUI/models/checkpoints/
COPY docker_models/loras/chad_sd1.5.safetensors /app/ComfyUI/models/loras/
```

**Note:** If you skip this step, you'll need to upload models to RunPod separately.

## Step 2: Build and Push Docker Image

Simply run the build script:

```bash
build_and_push_comfyui.bat
```

This will:
1. Check Docker is running
2. Ask for your DockerHub username
3. Build the Docker image (15-30 minutes)
4. Optionally push to DockerHub (10-20 minutes)

**Important:** Save the image name shown at the end!
Example: `yourusername/comfyui-morph:latest`

## Step 3: Create RunPod API Key

1. Go to https://www.runpod.io/console/user/settings
2. Click **"API Keys"** tab
3. Click **"Create API Key"**
4. Name it: `morph-comfyui`
5. **Copy and save the key** - you won't see it again!

## Step 4: Create RunPod Serverless Endpoint

1. Go to https://www.runpod.io/console/serverless

2. Click **"+ New Endpoint"**

3. **Configure the endpoint:**
   - **Name:** `morph-comfyui-endpoint`
   - **Docker Image:** `yourusername/comfyui-morph:latest`
   - **GPU Type:** Select based on budget
     - RTX 4090: ~$0.35/hr (recommended)
     - RTX 4060 Ti: ~$0.15/hr (cheaper)
     - A100: ~$1.00/hr (fastest)
   
4. **Advanced Settings:**
   - **Container Disk:** 20 GB
   - **Idle Timeout:** 5 seconds
   - **Max Workers:** 1 (increase later if needed)
   - **Environment Variables:** None needed

5. Click **"Deploy"**

6. **Copy the Endpoint ID** from the endpoint details page
   - It looks like: `abc123def456`

## Step 5: Configure Your Morph App

Add to your `.env` file:

```bash
# RunPod Configuration
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

## Step 6: Test the Setup

Run the test script:

```bash
python test_runpod_comfyui.py
```

This will:
1. Check endpoint health
2. Run a test workflow
3. Display results

## Step 7: Integrate with Your App

Use the client in your app:

```python
from runpod_comfyui_client import RunPodComfyUIClient
import os

# Initialize client
client = RunPodComfyUIClient(
    api_key=os.getenv("RUNPOD_API_KEY"),
    endpoint_id=os.getenv("RUNPOD_ENDPOINT_ID")
)

# Run FaceDetailer workflow
result = client.run_facedetailer(
    input_image="path/to/image.jpg",
    prompt="chad, male model, perfect face",
    denoise=0.55,
    steps=25
)

if result["status"] == "success":
    output_image = result["output"]["image"]
    print(f"Success! Generated image: {output_image}")
else:
    print(f"Error: {result['message']}")
```

## Troubleshooting

### Build Failed

**Problem:** Docker build fails
**Solution:**
- Make sure Docker Desktop is running
- Try: `docker system prune -a` to free space
- Check internet connection

### Push Failed

**Problem:** Docker push fails to DockerHub
**Solution:**
- Login to DockerHub: `docker login`
- Make sure username is correct
- Check DockerHub storage limits

### Endpoint Won't Start

**Problem:** RunPod endpoint stuck in "initializing"
**Solution:**
- Check Docker image name is correct
- Verify image exists on DockerHub
- Try smaller GPU type first
- Check RunPod status page

### Workflow Fails on RunPod

**Problem:** Health check OK but workflow fails
**Solution:**
- Check models are included in Docker image OR
- Upload models to RunPod storage
- Verify workflow JSON is valid
- Check logs in RunPod console

## Cost Estimation

### One-time Costs:
- Build time: FREE (local computer)
- DockerHub storage: FREE (up to 1 image)

### Ongoing Costs (Pay-per-second):
- RTX 4090: ~$0.001/second = ~$0.02-0.05 per generation
- Idle time: $0 (with 5s timeout)
- Storage: ~$0.02/GB/month

### Example Monthly Cost:
- 1000 generations/month
- RTX 4090
- 30s average per generation
- **Total: ~$35/month**

## Next Steps

1. ✅ Test with different prompts
2. ✅ Adjust denoise/steps for quality vs speed
3. ✅ Add more workflows (eyes, nose, etc.)
4. ✅ Monitor costs in RunPod dashboard
5. ✅ Scale up workers as needed

## Common Issues & Solutions

### Issue: "Missing node" errors
**Solution:**  
- Verify Impact-Pack and Impact-Subpack are in Dockerfile
- Rebuild Docker image

### Issue: High costs
**Solution:**
- Reduce max workers
- Increase idle timeout slightly
- Use cheaper GPU for testing
- Enable spot instances (50-70% cheaper)

### Issue: Slow cold starts
**Solution:**
- Models are already pre-loaded in Docker image
- First call may take 20-30s (normal)
- Subsequent calls are much faster

### Issue: Need different models
**Solution:**
1. Add models to `docker_models/` folder
2. Update Dockerfile COPY lines
3. Rebuild and push image
4. Update RunPod endpoint to new image

## Support Resources

- **RunPod Docs:** https://docs.runpod.io/
- **ComfyUI Docs:** https://github.com/comfyanonymous/ComfyUI
- **Impact Pack:** https://github.com/ltdrdata/ComfyUI-Impact-Pack
- **DockerHub:** https://hub.docker.com/

## Summary Checklist

- [ ] Docker Desktop installed and running
- [ ] DockerHub account created
- [ ] RunPod account created
- [ ] Models prepared (optional)
- [ ] Docker image built and pushed
- [ ] RunPod API key generated
- [ ] Serverless endpoint created
- [ ] .env file configured
- [ ] Test script run successfully
- [ ] Client integrated in app

**Estimated Time:** 30-45 minutes for first-time setup

**Congratulations!** 🎉 You now have ComfyUI running on RunPod serverless with all required nodes pre-installed!
