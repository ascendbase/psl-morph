# RunPod RTX 5090 Setup Guide

This guide will help you connect your Face Morphing App to your rented RTX 5090 RunPod.

## 🚀 Quick Setup

Based on your RunPod connection details:
- **Pod IP**: `149.36.1.79`
- **SSH Port**: `33805`
- **Jupyter Lab**: Available on port `8888`

## Step 1: Set Up ComfyUI on Your RunPod

### 1.1 Connect to Your Pod
You can connect via:
- **Web Terminal** (easiest - click "Start" in your RunPod dashboard)
- **SSH**: `ssh root@149.36.1.79 -p 33805`
- **Jupyter Lab**: Access via the provided link

### 1.2 Install ComfyUI
```bash
# Connect to your pod terminal and run:
cd /workspace

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Install additional nodes for face processing
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/Gourieff/comfyui-reactor-node.git
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git

# Install dependencies for the nodes
cd ../
pip install -r custom_nodes/comfyui-reactor-node/requirements.txt
```

### 1.3 Upload Your Models
```bash
# Create model directories
mkdir -p models/checkpoints
mkdir -p models/loras

# Upload your models (you can use the Jupyter Lab file browser or wget)
# For your base model:
cd models/checkpoints
# Upload real-dream-15.safetensors here

# For your LoRA:
cd ../loras
# Upload chad_sd1.5.safetensors here
```

### 1.4 Start ComfyUI with API
```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**Important**: Keep this terminal running! ComfyUI needs to stay active.

## Step 2: Configure Your Local App

### 2.1 Create Environment File
```bash
# In your local Face Morphing App directory
cp .env.runpod.example .env
```

### 2.2 Edit .env File
```bash
# Enable RunPod Pod mode
USE_CLOUD_GPU=true
USE_RUNPOD_POD=true

# Your RunPod connection details
RUNPOD_POD_URL=149.36.1.79
RUNPOD_POD_PORT=8188

# Database and other settings
DATABASE_URL=sqlite:///face_morph.db
SECRET_KEY=your_secret_key_here
```

### 2.3 Test Connection
```bash
# Test the connection
python test_runpod_pod.py
```

## Step 3: Advanced Setup (Optional)

### 3.1 Set Up Persistent Storage
```bash
# On your RunPod, create a startup script
nano /workspace/startup.sh
```

Add this content:
```bash
#!/bin/bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 &
echo "ComfyUI started on port 8188"
```

Make it executable:
```bash
chmod +x /workspace/startup.sh
```

### 3.2 Auto-start ComfyUI
Add to your pod's startup commands in RunPod dashboard:
```bash
/workspace/startup.sh
```

## Step 4: Upload Your Custom Models

### 4.1 Via Jupyter Lab (Recommended)
1. Open Jupyter Lab: `http://149.36.1.79:8888` (use the link from your RunPod dashboard)
2. Navigate to `ComfyUI/models/checkpoints/`
3. Upload `real-dream-15.safetensors`
4. Navigate to `ComfyUI/models/loras/`
5. Upload `chad_sd1.5.safetensors`

### 4.2 Via Command Line
```bash
# If you have your models on a cloud service
cd /workspace/ComfyUI/models/checkpoints
wget "https://your-model-url.com/real-dream-15.safetensors"

cd ../loras
wget "https://your-lora-url.com/chad_sd1.5.safetensors"
```

## Step 5: Test Your Setup

### 5.1 Verify ComfyUI is Running
Visit: `http://149.36.1.79:8188` in your browser
You should see the ComfyUI interface.

### 5.2 Test from Your App
```bash
# In your local app directory
python app.py
```

Visit `http://localhost:5000` and try uploading an image.

## 🔧 Troubleshooting

### ComfyUI Won't Start
```bash
# Check if port 8188 is already in use
netstat -tulpn | grep 8188

# Kill any existing process
pkill -f "python main.py"

# Restart ComfyUI
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

### Connection Refused
1. **Check ComfyUI is running**: Visit `http://149.36.1.79:8188`
2. **Check firewall**: RunPod should handle this automatically
3. **Verify pod is active**: Check your RunPod dashboard

### Models Not Loading
```bash
# Check model files exist
ls -la /workspace/ComfyUI/models/checkpoints/
ls -la /workspace/ComfyUI/models/loras/

# Check file permissions
chmod 644 /workspace/ComfyUI/models/checkpoints/*
chmod 644 /workspace/ComfyUI/models/loras/*
```

### Out of Memory
```bash
# Check GPU memory
nvidia-smi

# Reduce batch size or image resolution in your workflow
```

## 💡 Pro Tips

### 1. Keep Your Pod Running
- RunPod charges by the hour while your pod is active
- Stop the pod when not in use to save money
- Your files in `/workspace` persist between stops/starts

### 2. Monitor Usage
```bash
# Check GPU usage
watch -n 1 nvidia-smi

# Check system resources
htop
```

### 3. Backup Your Setup
```bash
# Create a backup of your ComfyUI setup
cd /workspace
tar -czf comfyui_backup.tar.gz ComfyUI/
```

### 4. Update Models
```bash
# To update your LoRA or base model, just replace the files
cd /workspace/ComfyUI/models/loras
rm chad_sd1.5.safetensors
# Upload new version
```

## 📊 Cost Optimization

### RTX 5090 Pricing
- **Hourly Rate**: ~$0.50-$1.00/hour (varies by availability)
- **Recommended Usage**: Start pod only when processing images
- **Auto-stop**: Set up auto-stop after inactivity

### Efficient Workflow
1. **Batch Processing**: Process multiple images at once
2. **Quick Testing**: Use lower resolution for testing
3. **Scheduled Processing**: Process during off-peak hours

## 🔒 Security Notes

- Your pod has a public IP - don't store sensitive data
- Use strong passwords if you set up additional services
- Monitor your usage to avoid unexpected charges

## 📞 Support

### RunPod Issues
- Check RunPod status page
- Contact RunPod support for pod-specific issues

### App Integration Issues
- Check the logs: `tail -f /workspace/ComfyUI/comfyui.log`
- Test connection: `curl http://149.36.1.79:8188/system_stats`
- Verify your `.env` configuration

---

**Your RTX 5090 is ready to morph faces! 🚀**

The RTX 5090 provides excellent performance for AI image generation with:
- **48GB VRAM**: Handle large images and complex workflows
- **High Performance**: Fast generation times
- **Latest Architecture**: Optimized for AI workloads