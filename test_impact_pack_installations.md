# Impact Pack Installation Testing Guide

Test these methods on your local ComfyUI to find which one works, then we'll use it in the Docker image.

## Method 1: ComfyUI Manager (Recommended)
```bash
# Start your ComfyUI
# Go to http://localhost:8188
# Click "Manager" button
# Search for "ComfyUI-Impact-Pack"
# Click "Install"
# Restart ComfyUI
```

## Method 2: Git Clone + Manual Dependencies
```bash
cd your_comfyui_folder/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack
pip install -r requirements.txt
# Restart ComfyUI
```

## Method 3: Pre-install Dependencies First
```bash
# Install dependencies BEFORE cloning
pip install opencv-python-headless ultralytics segment-anything
pip install scipy scikit-image insightface onnxruntime
pip install mediapipe albumentations kornia timm addict yapf

# Then clone
cd your_comfyui_folder/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
# Restart ComfyUI (skip requirements.txt)
```

## Method 4: Conda Environment (if you use conda)
```bash
conda create -n impact_test python=3.10
conda activate impact_test
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install opencv-python-headless ultralytics segment-anything
cd your_comfyui_folder/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack
pip install -r requirements.txt
```

## Method 5: Minimal Dependencies Only
```bash
# Install only the absolute minimum
pip install opencv-python-headless
pip install ultralytics
pip install segment-anything

cd your_comfyui_folder/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
# Skip requirements.txt entirely
# Restart ComfyUI
```

## Testing Steps:
1. Try each method one by one
2. After each attempt, restart ComfyUI
3. Check the console for errors
4. Try loading your workflow_facedetailer.json
5. Note which method works without import errors

## What to Look For:
✅ **Success:** "ComfyUI-Impact-Pack: loaded successfully"
❌ **Failure:** "ModuleNotFoundError" or "Failed to import"

## Report Back:
Tell me which method worked, and I'll create the perfect Dockerfile based on that approach!
