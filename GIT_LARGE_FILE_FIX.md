# Git Large File Push Fix
## Solution: Push Only Essential Files

## Problem
- Repository size: **3.67 GiB** 
- GitHub limit: **1 GB soft / 5 GB hard**
- Push failed with: "HTTP 500 - The remote end hung up unexpectedly"

## Quick Fix: Push Only Docker Files

### Step 1: Add .gitignore (if missing)

Check if `.gitignore` exists, if not create it:

```cmd
echo "# Large model files
base_models/
lora/
instance/
outputs/
uploads/
facial_evaluations/
docker_models/
*.safetensors
*.ckpt
*.pt
*.pth
*.bin
*.log
face_morph.db" > .gitignore
```

### Step 2: Push Only Essential Files

```cmd
# Add only the Docker setup files
git add Dockerfile.runpod.comfyui
git add .github/workflows/build-docker.yml
git add GITHUB_ACTIONS_COMPLETE_SETUP.md
git add workflow_facedetailer_requirements.md
git add runpod_comfyui_client.py
git add test_runpod_comfyui.py
git add FIX_DOCKER_BUILD_MEMORY.md
git add DOCKER_BUILD_FIX.md
git add check_docker.bat
git add build_and_push_comfyui.bat

# Commit and push
git commit -m "Add RunPod ComfyUI Docker setup with Impact-Pack"
git push origin main
```

### Step 3: Verify Success

Check GitHub Actions:
- Go to: https://github.com/ascendbase/psl-morph/actions
- You should see the Docker build workflow running

## Alternative: Remove Large Files from History

If the minimal push doesn't work, remove large files from git history:

```cmd
# Remove large directories from git but keep locally
git rm -r --cached base_models/
git rm -r --cached lora/
git rm -r --cached instance/
git rm -r --cached outputs/
git rm -r --cached uploads/

# Commit the cleanup
git add .gitignore
git commit -m "Remove large model files from git history"

# Force push (⚠️ This rewrites history - only do if needed)
git push origin main --force
```

## Why This Works

- **Minimal files**: Only ~1-2 MB of code files
- **No models**: Models are downloaded in Docker build
- **Clean repository**: Under GitHub's size limit
- **GitHub Actions**: Builds with all dependencies automatically

## Expected Result

After successful push:
1. ✅ GitHub Actions starts building Docker image
2. ✅ Image appears on DockerHub: `ascendbase/comfyui-morph:latest`
3. ✅ Ready for RunPod deployment
4. ✅ All workflow requirements met (Impact-Pack + Impact-Subpack)

## Files Being Pushed

These are the essential files for the Docker setup:
- `Dockerfile.runpod.comfyui` - ComfyUI with Impact-Pack
- `.github/workflows/build-docker.yml` - GitHub Actions build
- `runpod_comfyui_client.py` - Python client
- `test_runpod_comfyui.py` - Test script
- Setup guides and documentation

The large model files don't need to be in Git - they're downloaded during the Docker build!
