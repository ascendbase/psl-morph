# Workflow FaceDetailer Requirements Analysis

## Workflow File
`D:\Morph-app\comfyui_workflows\workflow_facedetailer.json`

## Node Analysis

### Standard ComfyUI Nodes (Built-in)
These nodes come with ComfyUI by default and require no additional installation:

1. **CheckpointLoaderSimple** - Loads SD checkpoint models
2. **LoraLoader** - Loads LoRA models
3. **CLIPTextEncode** - Encodes text prompts
4. **LoadImage** - Loads input images
5. **SaveImage** - Saves output images

### Custom Nodes Required

This workflow requires **TWO** related custom node packages:

#### 1. ComfyUI-Impact-Pack
Repository: https://github.com/ltdrdata/ComfyUI-Impact-Pack

**Nodes Used:**
1. **UltralyticsDetectorProvider** (Node 6)
   - Purpose: Face detection using YOLO models
   - Model used: `bbox/face_yolov8m.pt`

2. **SAMLoader** (Node 7)
   - Purpose: Loads SAM (Segment Anything Model) for segmentation
   - Model used: `sam_vit_b_01ec64.pth`

3. **FaceDetailer** (Node 8)
   - Purpose: Main face detailing/inpainting node
   - Combines detection, segmentation, and inpainting

#### 2. ComfyUI-Impact-Subpack
Repository: https://github.com/ltdrdata/ComfyUI-Impact-Subpack

**Purpose:** 
- Extension package for Impact Pack that provides additional detection/segmentation capabilities
- Required dependency for Impact Pack to work properly
- Manages model whitelists and ultralytics model paths

## Installation Instructions

### Method 1: ComfyUI Manager (Recommended)
```bash
# If ComfyUI Manager is installed:
# 1. Open ComfyUI web interface
# 2. Click "Manager" button
# 3. Search for "ComfyUI-Impact-Pack"
# 4. Click Install
# 5. Restart ComfyUI
```

### Method 2: Manual Installation
```bash
cd ComfyUI/custom_nodes

# Install Impact Pack
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack
pip install -r requirements.txt
cd ..

# Install Impact Subpack
git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git
cd ComfyUI-Impact-Subpack
pip install -r requirements.txt

# Restart ComfyUI
```

### Method 3: Windows Portable
```bash
cd ComfyUI_windows_portable\ComfyUI\custom_nodes

# Install Impact Pack
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack
..\..\..\.python_embeded\python.exe -m pip install -r requirements.txt
cd ..

# Install Impact Subpack
git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git
cd ComfyUI-Impact-Subpack
..\..\..\.python_embeded\python.exe -m pip install -r requirements.txt
```

## Required Models

After installing ComfyUI-Impact-Pack, you need these models:

### 1. Face Detection Model
- **File**: `face_yolov8m.pt`
- **Location**: `ComfyUI/models/ultralytics/bbox/`
- **Download**: Automatically downloaded by Impact Pack on first use, or manually from:
  - https://github.com/ultralytics/assets/releases

### 2. SAM Model
- **File**: `sam_vit_b_01ec64.pth`
- **Location**: `ComfyUI/models/sams/`
- **Download**: 
  - https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
  - Or use ComfyUI Manager to download

### 3. Checkpoint Model
- **File**: `real-dream-15.safetensors`
- **Location**: `ComfyUI/models/checkpoints/`
- **Note**: This is your SD 1.5 model (not part of Impact Pack)

### 4. LoRA Model
- **File**: `chad_sd1.5.safetensors`
- **Location**: `ComfyUI/models/loras/`
- **Note**: Your custom LoRA (not part of Impact Pack)

## Dependencies

ComfyUI-Impact-Pack dependencies (installed via requirements.txt):
- ultralytics
- segment-anything
- piexif
- scipy
- cv2 (opencv-python)

## Verification

To verify the installation:

1. Start ComfyUI
2. Check console for errors related to Impact Pack
3. Load the workflow_facedetailer.json
4. All nodes should appear without "missing node" errors
5. Check if model files are downloaded to correct locations

## Troubleshooting

### "Missing node" errors
- Ensure ComfyUI-Impact-Pack is installed in `custom_nodes` folder
- Restart ComfyUI after installation

### Model download errors
- Impact Pack usually auto-downloads models on first use
- Manually place models in correct directories if auto-download fails
- Check internet connection and firewall settings

### Import errors
- Run pip install again: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

## Summary

**Custom Node Packages Required:**
- ✅ ComfyUI-Impact-Pack (v8.15.3 or higher)
- ✅ ComfyUI-Impact-Subpack (v1.3.2 or higher)

**Total Model Requirements:**
- Face detector: face_yolov8m.pt (auto-downloaded)
- Segmentation: sam_vit_b_01ec64.pth  
- Checkpoint: real-dream-15.safetensors (your model)
- LoRA: chad_sd1.5.safetensors (your model)

## For RunPod Serverless Deployment

See the companion guide: `RUNPOD_COMFYUI_DEPLOYMENT_GUIDE.md` for instructions on creating a Docker image with all nodes and models pre-installed for serverless GPU usage.
