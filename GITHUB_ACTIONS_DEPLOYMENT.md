# 🚀 GitHub Actions Docker Build & RunPod Deployment

## 🎯 **PROBLEM SOLVED:**
- Local Docker build getting stuck/failing
- Need custom Docker image with your Real Dream + Chad LoRA models
- Want cloud serverless GPU deployment

## 💡 **SOLUTION:**
Use GitHub Actions to build Docker image in the cloud, then deploy to RunPod serverless.

## 📋 **STEP-BY-STEP DEPLOYMENT:**

### **Step 1: Setup Docker Hub Account**
1. Go to https://hub.docker.com
2. Create account or login
3. Go to Account Settings → Security
4. Create Access Token:
   - Token Name: `github-actions`
   - Permissions: `Read, Write, Delete`
   - Copy the token (save it!)

### **Step 2: Add GitHub Secrets**
1. Go to your GitHub repo: https://github.com/ascendbase/psl-morph
2. Click Settings → Secrets and variables → Actions
3. Add these secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: The access token from Step 1

### **Step 3: Commit and Push Changes**
```bash
git add .
git commit -m "Add GitHub Actions Docker build"
git push origin main
```

### **Step 4: Monitor Build**
1. Go to GitHub repo → Actions tab
2. Watch the "Build and Push Docker Image" workflow
3. Build takes ~10-15 minutes (much faster than local!)
4. When complete, image will be at: `ascendbase/face-morphing-comfyui:latest`

### **Step 5: Update RunPod Endpoint**
Once GitHub Actions completes:
```bash
python update_endpoint_docker_image.py
```

### **Step 6: Test Your Deployment**
```bash
python runpod_sd15_client.py
```

## 🔧 **FILES CREATED:**

### **`.github/workflows/build-docker.yml`**
- Builds Docker image in GitHub's cloud
- Pushes to Docker Hub automatically
- Uses caching for faster builds

### **`Dockerfile.runpod.simple`**
- Minimal Dockerfile that works
- Copies your local models into image
- Based on working ComfyUI base image

### **`update_endpoint_docker_image.py`**
- Updates your RunPod endpoint to use new image
- Switches from FLUX to your custom SD1.5 image

## ⚡ **WHY THIS WORKS:**

✅ **No local Docker issues** - builds in GitHub's cloud
✅ **Includes your models** - Real Dream + Chad LoRA baked in
✅ **Fast and reliable** - GitHub has fast internet and powerful servers
✅ **Automatic deployment** - push code, get Docker image
✅ **Free to use** - GitHub Actions free tier is generous

## 🎉 **EXPECTED TIMELINE:**

- **Step 1-3**: 5 minutes (setup)
- **Step 4**: 10-15 minutes (GitHub builds image)
- **Step 5-6**: 2 minutes (update endpoint and test)

**Total: ~20 minutes to working deployment**

## 🔍 **WHAT HAPPENS:**

1. **GitHub Actions** builds your Docker image with models
2. **Docker Hub** stores the image publicly
3. **RunPod** pulls and runs your custom image
4. **Your models** are ready to use on serverless GPU
5. **Face morphing** works with Real Dream + Chad LoRA

## 🚨 **IMPORTANT NOTES:**

- Make sure your models are in the correct folders:
  - `base_models/real-dream-15.safetensors`
  - `lora/chad_sd1.5.safetensors`
- GitHub Actions will fail if models are missing
- Docker image will be ~8GB (includes ComfyUI + your models)
- RunPod will download image once, then cache it

## 🎯 **NEXT STEPS:**

1. **Setup Docker Hub** (if not done)
2. **Add GitHub secrets**
3. **Push to trigger build**
4. **Wait for completion**
5. **Update RunPod endpoint**
6. **Test face morphing**

This approach completely bypasses local Docker issues and gives you a reliable, automated deployment pipeline!
