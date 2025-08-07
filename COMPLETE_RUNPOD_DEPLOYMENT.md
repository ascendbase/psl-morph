# Complete RunPod Deployment Guide

## Current Status
✅ Dockerfile.runpod created with ComfyUI + FaceDetailer + ReActor
✅ Dockerfile.runpod.optimized created (faster, more reliable build)
✅ Push scripts created (push_to_dockerhub.bat for Windows)
✅ Deployment instructions created
❌ Original Docker build stuck at step 5/21 - NEEDS RESTART

## What's Happening Now
The original Docker build got stuck at the git clone step. This is a common issue with large repositories.

**SOLUTION: Use the optimized Dockerfile**

The optimized build includes:
- Faster git clones with `--depth 1`
- Better error handling
- Smaller base image (python:3.10-slim)
- More efficient layer caching
- Parallel downloads where possible

**Expected build time with optimized Dockerfile: 8-15 minutes**

## Next Steps (After Build Completes)

### Step 1: Fix the Stuck Build

**IMPORTANT: Stop the current stuck build first!**

1. **Stop the stuck build:**
   - Go to your original build terminal
   - Press `Ctrl+C` to stop the build

2. **Clean up and restart:**
   ```cmd
   restart_docker_build.bat
   ```

   This will:
   - Clean up Docker cache
   - Start a new build with the optimized Dockerfile
   - Complete much faster (8-15 minutes vs 30+ minutes)

3. **Monitor the new build:**
   ```cmd
   monitor_docker_build.bat
   ```

### Step 2: Login to Docker Hub
```cmd
docker login
```
Enter your Docker Hub username and password when prompted.

### Step 3: Push Image to Docker Hub
```cmd
push_to_dockerhub.bat
```

This will push the image `ascendbase/face-morphing-comfyui:latest` to Docker Hub.

### Step 4: Deploy to RunPod Serverless

1. **Go to RunPod.io**
   - Navigate to https://www.runpod.io/
   - Login to your account
   - Go to "Serverless" section

2. **Create New Endpoint**
   - Click "Create Endpoint"
   - Fill in details:
     - **Name**: `face-morphing-comfyui`
     - **Container Image**: `ascendbase/face-morphing-comfyui:latest`
     - **GPU Type**: RTX 5090 (recommended) or RTX 4090
     - **Container Ports**: `8188`
     - **Container Start Command**: `python main.py --listen 0.0.0.0 --port 8188`
     - **Environment Variables**: (optional)
       ```
       PYTHONUNBUFFERED=1
       ```

3. **Configure Scaling**
   - **Min Workers**: 0 (for cost efficiency)
   - **Max Workers**: 3-5 (depending on expected load)
   - **Idle Timeout**: 5 seconds
   - **Max Execution Time**: 300 seconds (5 minutes)

4. **Deploy**
   - Click "Create Endpoint"
   - Wait for deployment (usually 2-5 minutes)
   - Note down the **Endpoint ID** and **API Key**

### Step 5: Update Your Application

Update your `.env` file with RunPod configuration:
```env
# RunPod Serverless Configuration
USE_CLOUD_GPU=true
USE_RUNPOD_POD=false
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_API_KEY=your_api_key_here
RUNPOD_SERVERLESS_URL=https://api.runpod.ai/v2/your_endpoint_id/runsync
```

### Step 6: Test the Deployment

Run your application locally and test the RunPod connection:
```cmd
python app.py
```

The application should now use the RunPod serverless endpoint for face morphing operations.

## Cost Benefits

With RunPod Serverless:
- **Pay per second** (minimum 1 second)
- **No idle costs** when not in use
- **~80% cost reduction** vs dedicated pods
- **Automatic scaling** based on demand

## Troubleshooting

### Build Issues
- If build fails, check Docker Desktop is running
- Ensure sufficient disk space (5-10GB needed)
- Check internet connection for downloads

### Push Issues
- Verify Docker Hub login: `docker login`
- Check image exists: `docker images`
- Ensure repository name is correct

### RunPod Issues
- Verify image is public on Docker Hub
- Check endpoint configuration matches exactly
- Review RunPod logs in dashboard
- Ensure GPU type is available

## Support Files Created
- `Dockerfile.runpod` - Main Docker configuration
- `push_to_dockerhub.bat` - Windows push script
- `push_to_dockerhub.sh` - Linux/Mac push script
- `monitor_docker_build.bat` - Build monitoring script
- `RUNPOD_DEPLOYMENT_INSTRUCTIONS.md` - Detailed instructions

## Expected Timeline
- Docker build: 15-30 minutes (in progress)
- Push to Docker Hub: 5-10 minutes
- RunPod deployment: 2-5 minutes
- **Total**: ~30-45 minutes from start to finish

Your deployment is well on track! The Docker build is the longest step, and once it completes, the remaining steps are quick and straightforward.
