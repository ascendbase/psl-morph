# Use ComfyUI base image
FROM runpod/comfyui:latest

# Install additional dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install custom nodes
WORKDIR /workspace/ComfyUI/custom_nodes

# Install FaceDetailer node
RUN git clone https://github.com/BadCafeCode/masquerade-nodes-comfyui.git
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
RUN git clone https://github.com/WASasquatch/was-node-suite-comfyui.git

# Install ReActor if needed
RUN git clone https://github.com/Gourieff/comfyui-reactor-node.git
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui-reactor-node
RUN pip install -r requirements.txt

# Download models
WORKDIR /workspace/ComfyUI/models/checkpoints
RUN wget -O real-dream-15.safetensors "YOUR_DOWNLOAD_LINK_FOR_REAL_DREAM_MODEL"

WORKDIR /workspace/ComfyUI/models/loras
RUN wget -O chad_sd1.5.safetensors "YOUR_DOWNLOAD_LINK_FOR_CHAD_LORA"

# Download FaceDetailer models
WORKDIR /workspace/ComfyUI/models/ultralytics
RUN wget -O face_yolov8m.pt "https://github.com/Bing-su/sd-webui-models/raw/main/detection/bbox/face_yolov8m.pt"

WORKDIR /workspace/ComfyUI/models/sams
RUN wget -O sam_vit_b_01ec64.pth "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"

# Set up workflow templates
WORKDIR /workspace/ComfyUI
COPY workflows/ ./workflows/

# Expose port
EXPOSE 8188

# Start ComfyUI
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]