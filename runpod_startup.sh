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
