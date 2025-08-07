# 🚀 GitHub → RunPod Serverless Deployment (RECOMMENDED)

## 🎯 **SOLUTION: Use GitHub Sync + ComfyUI Manager**

Since you're using GitHub sync, we can fix the dependency issues by:
1. **Adding a startup script** that installs missing dependencies
2. **Using ComfyUI Manager** to properly install custom nodes
3. **Leveraging GitHub sync** for automatic updates

## 📋 **Step 1: Create Startup Script**

Create this file in your repo and commit it:

**File: `runpod_startup.sh`**
```bash
#!/bin/bash

echo "🚀 Starting RunPod ComfyUI with GitHub sync..."

# Install missing Python dependencies
echo "📦 Installing missing dependencies..."
pip install --no-cache-dir \
    opencv-python-headless \
    numba \
    scipy \
    scikit-image \
    segment-anything \
    ultralytics \
    insightface \
    onnxruntime \
    facexlib \
    gfpgan \
    realesrgan

# Navigate to ComfyUI directory
cd /workspace/ComfyUI

# Install ComfyUI Manager if not present
if [ ! -d "custom_nodes/ComfyUI-Manager" ]; then
    echo "📥 Installing ComfyUI Manager..."
    cd custom_nodes
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    cd ..
fi

# Create models directories
mkdir -p models/ultralytics models/sams

# Download required models
echo "📥 Downloading face detection models..."
cd models/ultralytics
wget -q -O face_yolov8m.pt "https://github.com/Bing-su/sd-webui-models/raw/main/detection/bbox/face_yolov8m.pt" || echo "Face model download failed"

cd ../sams
wget -q -O sam_vit_b_01ec64.pth "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" || echo "SAM model download failed"

cd /workspace/ComfyUI

echo "✅ Setup complete! Starting ComfyUI..."
python main.py --listen 0.0.0.0 --port 8188 --dont-print-server
```

## 📋 **Step 2: Update RunPod Serverless Configuration**

### **Option A: Use GitHub Template (RECOMMENDED)**

1. **Go to RunPod Console** → **Serverless** → **Your Endpoint**
2. **Click "Edit"**
3. **Set Container Image** to: `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04`
4. **Enable GitHub Integration:**
   - Repository: `ascendbase/psl-morph`
   - Branch: `main`
   - Access Token: Your GitHub token
5. **Set Startup Command:**
   ```bash
   chmod +x /workspace/runpod_startup.sh && /workspace/runpod_startup.sh
   ```

### **Option B: Manual Startup Script**

If GitHub sync isn't working, use this startup command:
```bash
cd /workspace && \
pip install opencv-python-headless numba scipy scikit-image segment-anything ultralytics insightface onnxruntime facexlib gfpgan realesrgan && \
git clone https://github.com/comfyanonymous/ComfyUI.git && \
cd ComfyUI && \
pip install -r requirements.txt && \
cd custom_nodes && \
git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
cd .. && \
mkdir -p models/ultralytics models/sams && \
wget -q -O models/ultralytics/face_yolov8m.pt "https://github.com/Bing-su/sd-webui-models/raw/main/detection/bbox/face_yolov8m.pt" && \
wget -q -O models/sams/sam_vit_b_01ec64.pth "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" && \
python main.py --listen 0.0.0.0 --port 8188 --dont-print-server
```

## 📋 **Step 3: Install Custom Nodes via ComfyUI Manager**

Once ComfyUI starts:

1. **Access ComfyUI Web Interface** (RunPod will provide the URL)
2. **Click "Manager" button** (should appear in the interface)
3. **Install Custom Nodes:**
   - Search for "Impact Pack" → Install
   - Search for "WAS Node Suite" → Install  
   - Search for "ReActor" → Install
   - Search for "Masquerade" → Install

4. **Restart ComfyUI** after installation

## 🔧 **Step 4: Configure Environment Variables**

In your RunPod serverless endpoint, set these environment variables:

```bash
PYTHONUNBUFFERED=1
COMFYUI_PORT=8188
CUDA_VISIBLE_DEVICES=0
```

## 🎯 **Expected Results**

After this setup:
- ✅ All Python dependencies installed (cv2, numba, etc.)
- ✅ ComfyUI Manager available for easy node management
- ✅ Custom nodes properly installed and working
- ✅ Face detection models downloaded
- ✅ GitHub sync keeps everything updated

## 🔍 **Verify Installation**

Check the RunPod logs for:
```
✅ Installing missing dependencies...
✅ Installing ComfyUI Manager...
✅ Downloading face detection models...
✅ Setup complete! Starting ComfyUI...
✅ Import times for custom nodes:
✅   ComfyUI-Impact-Pack: loaded successfully
```

## 💡 **Pro Tips**

1. **Use ComfyUI Manager** - Much more reliable than manual git clones
2. **GitHub sync** - Automatically pulls your latest code changes
3. **Persistent storage** - Models stay downloaded between runs
4. **Environment variables** - Configure settings without code changes

## 🆘 **Troubleshooting**

If custom nodes still fail:
1. **Check ComfyUI Manager logs** in the web interface
2. **Manually install** problematic nodes via Manager
3. **Restart the endpoint** after installing nodes
4. **Check model paths** are correct

---

**This approach is much more reliable and maintainable than hardcoded Dockerfile installations!** 🚀
