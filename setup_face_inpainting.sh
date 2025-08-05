#!/bin/bash

echo "🎭 Face Inpainting Setup Script"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "This script will help you set up the Face Inpainting workflow"
echo "which replaces ReActor with better face masking and compositing."
echo ""

echo "📋 What this workflow does:"
echo "1. Detects face area using SAM (Segment Anything Model)"
echo "2. Creates precise mask around the face"
echo "3. Inpaints only the face area with your LoRA"
echo "4. Seamlessly blends with original image"
echo ""

read -p "Enter your ComfyUI directory path (e.g., /home/user/ComfyUI): " comfyui_path

if [ ! -d "$comfyui_path" ]; then
    echo -e "${RED}❌ ComfyUI directory not found: $comfyui_path${NC}"
    echo "Please check the path and try again."
    exit 1
fi

echo -e "${GREEN}✅ ComfyUI directory found: $comfyui_path${NC}"

echo ""
echo "📦 Installing SAM extension for face detection..."
cd "$comfyui_path/custom_nodes"

if [ -d "comfyui_segment_anything" ]; then
    echo -e "${YELLOW}⚠️  SAM extension already exists, updating...${NC}"
    cd comfyui_segment_anything
    git pull
else
    echo "📥 Downloading SAM extension..."
    git clone https://github.com/storyicon/comfyui_segment_anything.git
    cd comfyui_segment_anything
fi

echo "📦 Installing SAM dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install SAM dependencies${NC}"
    echo "Try running: pip install segment-anything opencv-python"
    exit 1
fi

echo -e "${GREEN}✅ SAM extension installed successfully${NC}"

echo ""
echo "📥 The SAM model will be downloaded automatically on first use (~2GB)"
echo "This may take a few minutes the first time you run the workflow."

echo ""
echo "🔧 Next steps:"
echo "1. Restart ComfyUI to load the new extension"
echo "2. Start ComfyUI with: python main.py --listen 127.0.0.1 --port 8188"
echo "3. Test the workflow manually in ComfyUI first"
echo "4. Run the Face Morphing Web App: python app.py"
echo ""

echo -e "${GREEN}✅ Face Inpainting setup complete!${NC}"
echo "The app is now configured to use face masking instead of ReActor."
echo ""