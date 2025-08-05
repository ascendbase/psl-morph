#!/bin/bash
# Setup script for ComfyUI on RunPod RTX 5090
# Run this script on your RunPod terminal

echo "🚀 Setting up ComfyUI on RTX 5090 RunPod..."

# Check if we're in the right directory
if [ ! -d "/workspace" ]; then
    echo "Creating workspace directory..."
    mkdir -p /workspace
fi

cd /workspace

# Check if ComfyUI already exists
if [ -d "ComfyUI" ]; then
    echo "✅ ComfyUI directory already exists"
    cd ComfyUI
else
    echo "📥 Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
fi

# Install dependencies
echo "📦 Installing ComfyUI dependencies..."
pip install -r requirements.txt

# Install additional useful packages
echo "📦 Installing additional packages..."
pip install opencv-python pillow requests

# Create model directories
echo "📁 Creating model directories..."
mkdir -p models/checkpoints
mkdir -p models/loras
mkdir -p models/vae
mkdir -p models/controlnet
mkdir -p models/upscale_models

# Install useful custom nodes
echo "🔧 Installing custom nodes..."
cd custom_nodes

# ComfyUI Manager (for easy node management)
if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# ReActor (face swapping)
if [ ! -d "comfyui-reactor-node" ]; then
    git clone https://github.com/Gourieff/comfyui-reactor-node.git
    cd comfyui-reactor-node
    pip install -r requirements.txt
    cd ..
fi

# Impact Pack (includes FaceDetailer)
if [ ! -d "ComfyUI-Impact-Pack" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
    cd ComfyUI-Impact-Pack
    pip install -r requirements.txt
    cd ..
fi

# ControlNet Auxiliary Preprocessors
if [ ! -d "comfyui_controlnet_aux" ]; then
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
    cd comfyui_controlnet_aux
    pip install -r requirements.txt
    cd ..
fi

cd ..

# Check GPU
echo "🔍 Checking GPU..."
nvidia-smi

# Create startup script
echo "📝 Creating startup script..."
cat > start_comfyui.sh << 'EOF'
#!/bin/bash
cd /workspace/ComfyUI
echo "🚀 Starting ComfyUI with API on RTX 5090..."
echo "Access ComfyUI at: http://149.36.1.79:8188"
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
EOF

chmod +x start_comfyui.sh

# Create model download script
echo "📝 Creating model download helper..."
cat > download_models.sh << 'EOF'
#!/bin/bash
echo "📥 Model Download Helper"
echo "Upload your models using one of these methods:"
echo ""
echo "1. Jupyter Lab (Recommended):"
echo "   - Open: http://149.36.1.79:8888"
echo "   - Navigate to ComfyUI/models/checkpoints/"
echo "   - Upload real-dream-15.safetensors"
echo "   - Navigate to ComfyUI/models/loras/"
echo "   - Upload chad_sd1.5.safetensors"
echo ""
echo "2. Command line (if you have URLs):"
echo "   cd /workspace/ComfyUI/models/checkpoints"
echo "   wget 'https://your-model-url.com/real-dream-15.safetensors'"
echo "   cd ../loras"
echo "   wget 'https://your-lora-url.com/chad_sd1.5.safetensors'"
echo ""
echo "3. SCP from local machine:"
echo "   scp -P 33805 real-dream-15.safetensors root@149.36.1.79:/workspace/ComfyUI/models/checkpoints/"
echo "   scp -P 33805 chad_sd1.5.safetensors root@149.36.1.79:/workspace/ComfyUI/models/loras/"
EOF

chmod +x download_models.sh

echo ""
echo "✅ ComfyUI setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your models: ./download_models.sh"
echo "2. Start ComfyUI: ./start_comfyui.sh"
echo "3. Access ComfyUI: http://149.36.1.79:8188"
echo ""
echo "🔗 Useful links:"
echo "   ComfyUI Web UI: http://149.36.1.79:8188"
echo "   Jupyter Lab: http://149.36.1.79:8888"
echo ""
echo "💡 Pro tip: Keep this terminal open while ComfyUI is running!"