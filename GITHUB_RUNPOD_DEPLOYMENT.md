# GitHub → RunPod Serverless Deployment Guide

## 🎯 Overview
Instead of building Docker images locally (which failed), we'll use RunPod's GitHub integration to deploy directly from your repository. This is much faster and more reliable!

## ✅ What You Have
- Your code is already on GitHub: `https://github.com/ascendbase/psl-morph.git`
- RunPod offers direct GitHub deployment
- No need to build Docker images locally!

## 🚀 Step-by-Step GitHub Deployment

### Step 1: Prepare Your Repository
Your repository already has everything needed:
- ✅ `Dockerfile.runpod` (for RunPod to build)
- ✅ ComfyUI workflows
- ✅ Python application code
- ✅ Requirements files

### Step 2: Create RunPod Serverless Endpoint from GitHub

1. **Go to RunPod Console**
   - Visit: https://www.runpod.io/console/serverless
   - Click "Deploy a New Serverless Endpoint"

2. **Choose "Import Git Repository"**
   - Click "Connect GitHub" (as shown in your screenshot)
   - Authorize RunPod to access your GitHub account

3. **Select Your Repository**
   - Choose: `ascendbase/psl-morph`
   - Branch: `main` (or your default branch)

4. **Configure Build Settings**
   - **Dockerfile Path**: `Dockerfile.runpod`
   - **Build Context**: `/` (root directory)
   - **Build Arguments**: (leave empty)

5. **Configure Endpoint Settings**
   - **Endpoint Name**: `face-morphing-comfyui`
   - **GPU Type**: RTX 4090 or A100
   - **Container Disk**: 20GB
   - **Max Workers**: 3-5
   - **Idle Timeout**: 5 seconds
   - **Max Execution Time**: 300 seconds

6. **Environment Variables** (if needed)
   ```
   PYTHONUNBUFFERED=1
   ```

### Step 3: Deploy and Get Endpoint Details

After deployment, you'll get:
- **Endpoint ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **API URL**: `https://api.runpod.ai/v2/your-endpoint-id`
- **API Key**: Your RunPod API key

## 🔧 Advantages of GitHub Deployment

### ✅ Benefits
- **No local Docker build** (eliminates I/O errors)
- **Automatic rebuilds** when you push to GitHub
- **RunPod's optimized build environment**
- **Faster deployment** (RunPod has better infrastructure)
- **Version control integration**
- **No need to push to Docker Hub**

### ⚡ Speed Comparison
- **Local Docker build**: 2+ hours (often fails)
- **GitHub → RunPod**: 10-20 minutes (reliable)

## 📋 Next Steps After Deployment

### 1. Test the Endpoint
```python
import requests

# Test endpoint
url = "https://api.runpod.ai/v2/your-endpoint-id/run"
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}

data = {
    "input": {
        "workflow": {
            # Your ComfyUI workflow here
        }
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 2. Update Your Railway App
Add these environment variables to your Railway app:
```env
RUNPOD_SERVERLESS_ENDPOINT=your-endpoint-id
RUNPOD_API_KEY=your-api-key
RUNPOD_SERVERLESS_URL=https://api.runpod.ai/v2/your-endpoint-id
```

### 3. Update Your Client Code
Use the serverless client code from `COMPLETE_INTEGRATION_GUIDE.md`

## 🎯 Expected Results

### Cost Savings
- **Before**: $648/month (hourly GPU)
- **After**: $4-40/month (serverless)
- **Savings**: 95-99% cost reduction!

### Performance
- **Build time**: 10-20 minutes (vs 2+ hours locally)
- **Reliability**: Much higher success rate
- **Maintenance**: Automatic updates from GitHub

## 🔄 Workflow Updates

When you make changes to your code:
1. Push to GitHub
2. RunPod automatically rebuilds the endpoint
3. New version is deployed automatically
4. No manual Docker builds needed!

## 🎉 Why This Approach is Better

1. **Eliminates Docker build issues** (I/O errors, timeouts)
2. **Faster deployment** (RunPod's infrastructure)
3. **Automatic CI/CD** (GitHub integration)
4. **Version control** (tied to your Git commits)
5. **Easier maintenance** (no local Docker management)
6. **Better reliability** (RunPod's build environment)

Your face morphing app will be profitable and scalable with this approach!
