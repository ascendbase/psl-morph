# 🎭 ComfyUI Face Masking Tutorial - Step by Step

Don't worry! I'll walk you through creating a face masking workflow in ComfyUI step by step. This will replace ReActor with better control.

## 🎯 **What We're Building**

Instead of ReActor face swapping, we want:
1. **Load your image**
2. **Generate new face** with your LoRA
3. **Detect face area** automatically
4. **Paste generated face** only in that area
5. **Blend seamlessly** with original

## 📋 **Step-by-Step Instructions**

### **Step 1: Open ComfyUI**
1. Start ComfyUI: `python main.py --listen 127.0.0.1 --port 8188`
2. Open browser: http://127.0.0.1:8188
3. You should see the ComfyUI interface

### **Step 2: Clear the Workspace**
1. **Select all nodes**: Ctrl+A (or Cmd+A on Mac)
2. **Delete everything**: Delete key
3. Now you have a clean workspace

### **Step 3: Add Basic Nodes**

#### **Add Checkpoint Loader**
1. **Right-click** in empty space
2. Go to: **loaders** → **CheckpointLoaderSimple**
3. Click to add the node
4. In the node, select: **real-dream-15.safetensors**

#### **Add LoRA Loader**
1. **Right-click** in empty space
2. Go to: **loaders** → **LoraLoader**
3. Connect **MODEL** and **CLIP** from CheckpointLoader to LoraLoader
4. In LoraLoader, select: **chad_sd1.5.safetensors**
5. Set strength_model: **0.8**
6. Set strength_clip: **0.85**

#### **Add Text Encoders**
1. **Right-click** → **conditioning** → **CLIPTextEncode**
2. Add **two** of these nodes
3. **First one** (positive): Type "chad, male model"
4. **Second one** (negative): Type "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face"
5. Connect **CLIP** from LoraLoader to both text encoders

#### **Add Load Image**
1. **Right-click** → **image** → **LoadImage**
2. This will load your uploaded photo

#### **Add VAE Encode**
1. **Right-click** → **latent** → **VAEEncode**
2. Connect **IMAGE** from LoadImage to **pixels**
3. Connect **VAE** from CheckpointLoader to **vae**

#### **Add KSampler**
1. **Right-click** → **sampling** → **KSampler**
2. Connect:
   - **MODEL** from LoraLoader
   - **positive** from first text encoder
   - **negative** from second text encoder
   - **latent_image** from VAEEncode
3. Set parameters:
   - **steps**: 20
   - **cfg**: 8.0
   - **sampler_name**: dpmpp_2m
   - **scheduler**: normal
   - **denoise**: 0.5 (we'll change this via the app)

#### **Add VAE Decode**
1. **Right-click** → **latent** → **VAEDecode**
2. Connect **samples** from KSampler
3. Connect **VAE** from CheckpointLoader

#### **Add Save Image**
1. **Right-click** → **image** → **SaveImage**
2. Connect **IMAGE** from VAEDecode

### **Step 4: Test Basic Workflow**
1. **Upload a test image** in LoadImage node
2. **Click Queue Prompt** (top right)
3. **Check if it generates** a full image
4. If it works, continue to Step 5

### **Step 5: Add Face Masking (Simple Version)**

Since you have Face Tools extension, let's try this:

#### **Option A: If you have Impact Pack**
1. **Right-click** → look for **Impact Pack** or **detector** nodes
2. Try to find: **UltralyticsDetectorProvider** or **FaceDetailer**
3. If found, add it between LoadImage and the compositing

#### **Option B: Simple Composite Method**
1. **Right-click** → **image** → look for **ImageComposite** or **ImageBlend**
2. Add this node after VAEDecode
3. Connect:
   - **destination**: Original image (from LoadImage)
   - **source**: Generated image (from VAEDecode)

#### **Option C: Manual Mask (Easiest)**
1. **Right-click** → **mask** → **LoadImageMask**
2. This lets you upload a black/white mask image
3. White = where to paste generated face
4. Black = keep original

### **Step 6: Export Your Workflow**
1. **Click the gear icon** (settings) in top right
2. **Enable "Enable Dev mode Options"**
3. **Click "Save (API Format)"** button
4. **Save as**: `my_face_workflow.json`
5. **Send me this file** and I'll integrate it into the app!

## 🔍 **What to Look For**

### **Face Detection Nodes**
Look for nodes with these names:
- **FaceDetailer**
- **UltralyticsDetectorProvider** 
- **SAMDetectorSegmented**
- **FaceAnalysis**
- **MediaPipeFaceMesh**

### **Compositing Nodes**
Look for:
- **ImageComposite**
- **ImageCompositeAbsolute**
- **ImageBlend**
- **MaskComposite**

### **Mask Nodes**
Look for:
- **LoadImageMask**
- **MaskToImage**
- **GrowMask**
- **ImageBlur** (for soft edges)

## 🆘 **If You Get Stuck**

### **Can't Find Face Detection Nodes?**
1. Check what extensions you have installed
2. Look in **custom_nodes** folder
3. Try the simple composite method instead

### **Workflow Won't Run?**
1. Make sure all connections are made (lines between nodes)
2. Check that model files are selected correctly
3. Try with a smaller, simpler workflow first

### **No Face Detection Available?**
We can use a **simple approach**:
1. Generate full image with your LoRA
2. Use basic **ImageComposite** node
3. Manually create a face mask (black/white image)
4. This still gives better control than ReActor

## 📤 **Send Me Your Results**

Once you have **any working workflow** (even without face detection), export the JSON and send it to me. I can:

1. **Clean up the workflow**
2. **Add it to the app**
3. **Make it work with your presets**
4. **Add face detection later** if needed

The goal is to get **something working** that gives you more control than ReActor, even if it's not perfect yet!

## 💡 **Quick Alternative**

If this seems too complex, we can also:
1. **Keep using ReActor** for now (it's working!)
2. **Focus on perfecting** your denoise levels (20%/50%/80%)
3. **Add face masking later** when you're more comfortable with ComfyUI

Your app is already working great with the extreme denoise range - the face masking is just an upgrade, not a necessity!