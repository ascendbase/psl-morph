# 🔧 RunPod Docker Image Fix - Complete Dependencies

## 🚨 **PROBLEM IDENTIFIED**

Your RunPod serverless endpoint is missing critical dependencies:
- `cv2` (OpenCV) - needed for ComfyUI-Impact-Pack (FaceDetailer)
- `numba` - needed for was-node-suite-comfyui
- Various other packages for face processing

## ✅ **SOLUTION: Build Custom Docker Image**

I've updated `Dockerfile.runpod` with all missing dependencies. Here's how to deploy it:

### **Step 1: Build the Docker Image**

```bash
# Build the image locally
docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:fixed .

# Or use the provided script
./push_to_dockerhub.sh
```

### **Step 2: Push to Docker Hub**

```bash
# Login to Docker Hub
docker login

# Push the image
docker push ascendbase/face-morphing-comfyui:fixed
```

### **Step 3: Update RunPod Serverless Endpoint**

1. **Go to RunPod Console** → **Serverless** → **Your Endpoint**
2. **Click "Edit"**
3. **Update Container Image** to: `ascendbase/face-morphing-comfyui:fixed`
4. **Save Changes**

## 🔧 **What the Fixed Dockerfile Includes**

### **System Dependencies:**
- OpenCV system libraries (`libgl1-mesa-glx`, `libsm6`, etc.)
- Build tools for compiling packages
- GTK libraries for GUI components

### **Python Dependencies:**
- `opencv-python-headless` - Computer vision (fixes cv2 error)
- `numba` - JIT compilation (fixes numba error)
- `scipy` - Scientific computing
- `scikit-image` - Image processing
- `segment-anything` - SAM model support
- `ultralytics` - YOLO models
- `insightface` - Face recognition
- `onnxruntime` - ONNX model inference
- `facexlib` - Face processing utilities
- `gfpgan` - Face restoration
- `realesrgan` - Image upscaling

### **ComfyUI Custom Nodes:**
- ✅ ComfyUI-Impact-Pack (FaceDetailer)
- ✅ masquerade-nodes-comfyui
- ✅ was-node-suite-comfyui
- ✅ comfyui-reactor-node

### **Pre-downloaded Models:**
- Face detection: `face_yolov8m.pt`
- Segmentation: `sam_vit_b_01ec64.pth`

## 🚀 **Quick Deploy Commands**

### **Windows (PowerShell):**
```powershell
# Build and push
docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:fixed .
docker push ascendbase/face-morphing-comfyui:fixed
```

### **Linux/Mac:**
```bash
# Use the provided script
chmod +x push_to_dockerhub.sh
./push_to_dockerhub.sh
```

## 📋 **Alternative: Use Pre-built Image**

If you don't want to build locally, you can use a pre-built image:

1. **Update your RunPod endpoint** to use: `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04`
2. **Add startup script** to install dependencies:

```bash
#!/bin/bash
pip install opencv-python-headless numba scipy scikit-image segment-anything ultralytics insightface onnxruntime facexlib gfpgan realesrgan
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
git clone https://github.com/WASasquatch/was-node-suite-comfyui.git
git clone https://github.com/BadCafeCode/masquerade-nodes-comfyui.git
cd ..
python main.py --listen 0.0.0.0 --port 8188
```

## 🎯 **Expected Result**

After deploying the fixed image:
- ✅ No more `cv2` import errors
- ✅ No more `numba` import errors
- ✅ ComfyUI-Impact-Pack loads successfully
- ✅ FaceDetailer nodes work properly
- ✅ Face morphing generations complete successfully

## 🔍 **Verify the Fix**

Check the RunPod logs after deployment. You should see:
```
✅ Import times for custom nodes:
✅   ComfyUI-Impact-Pack: loaded successfully
✅   was-node-suite-comfyui: loaded successfully
✅   masquerade-nodes-comfyui: loaded successfully
```

Instead of the previous import errors.

## 💡 **Pro Tips**

1. **Use the fixed image**: `ascendbase/face-morphing-comfyui:fixed`
2. **Monitor build time**: The image build takes 10-20 minutes
3. **Test locally first**: Build and test the image locally before pushing
4. **Keep backups**: Save your current endpoint settings before updating

## 🆘 **If Build Fails**

If Docker build fails locally:
1. **Increase Docker memory** to 8GB+
2. **Use the alternative startup script** method above
3. **Contact RunPod support** for pre-built ComfyUI images with dependencies

---

**This fix will resolve all the missing dependency errors and make your face morphing app fully functional!** 🚀
