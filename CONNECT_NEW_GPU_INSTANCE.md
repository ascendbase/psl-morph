# Connect Your New GPU Instance - Step by Step

## Step 1: Get Your GPU Instance Details
First, I need to know:
1. **What's the IP address** of your new GPU instance?
2. **What cloud provider** are you using? (RunPod, Vast.ai, etc.)
3. **Do you have SSH access** to the instance?

## Step 2: Install ComfyUI on Your GPU Instance

### Option A: If it's a fresh instance
SSH into your instance and run:
```bash
# Update system
apt update && apt upgrade -y

# Install Python and Git
apt install -y python3 python3-pip git

# Clone ComfyUI
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install requirements
pip install -r requirements.txt

# Install additional dependencies
pip install opencv-python ultralytics
```

### Option B: If ComfyUI is already installed
Just make sure it's updated:
```bash
cd /workspace/ComfyUI
git pull
pip install -r requirements.txt
```

## Step 3: Upload Your Models

You need to upload these files to your GPU instance:

### Base Model:
Upload `real-dream-15.safetensors` to:
```
/workspace/ComfyUI/models/checkpoints/real-dream-15.safetensors
```

### LoRA Model:
Upload `chad_sd1.5.safetensors` to:
```
/workspace/ComfyUI/models/loras/chad_sd1.5.safetensors
```

### Upload Methods:
1. **SCP** (if you have SSH):
   ```bash
   scp base_models/real-dream-15.safetensors root@YOUR_IP:/workspace/ComfyUI/models/checkpoints/
   scp lora/chad_sd1.5.safetensors root@YOUR_IP:/workspace/ComfyUI/models/loras/
   ```

2. **Web interface** (if your provider has one)

3. **wget** (if models are online):
   ```bash
   cd /workspace/ComfyUI/models/checkpoints/
   wget YOUR_MODEL_URL
   ```

## Step 4: Start ComfyUI on Your GPU Instance

SSH into your instance and run:
```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

You should see output like:
```
To see the GUI go to: http://0.0.0.0:8188
```

## Step 5: Test Direct Connection

From your local machine, test if you can reach ComfyUI:
```bash
curl http://YOUR_GPU_IP:8188/system_stats
```

Or open in browser: `http://YOUR_GPU_IP:8188`

## Step 6: Update Your App Configuration

Update your `.env` file:
```env
# GPU Instance Configuration
USE_CLOUD_GPU=false
COMFYUI_URL=http://YOUR_GPU_IP:8188
COMFYUI_TIMEOUT=300

# Keep other settings the same
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///face_morph.db
# ... rest of your config
```

## Step 7: Test Your App

1. **Restart your app**:
   ```bash
   # Stop current app (Ctrl+C in terminal)
   python app.py
   ```

2. **Test image generation**:
   - Go to http://localhost:5000
   - Upload an image
   - Try HTN/Chadlite/Chad transformation
   - Check if it uses your cloud GPU

## Step 8: Verify It's Working

You should see in your app logs:
```
GPU Provider: ComfyUI (URL: http://YOUR_GPU_IP:8188)
ComfyUI processing started...
```

And on your GPU instance, you should see ComfyUI processing the request.

## Troubleshooting

### If connection fails:
1. **Check firewall**: Make sure port 8188 is open
2. **Check ComfyUI**: Make sure it's running with `--listen 0.0.0.0`
3. **Check IP**: Make sure you're using the correct external IP
4. **Check provider**: Some providers block certain ports

### If models are missing:
```bash
# Check if models exist
ls -la /workspace/ComfyUI/models/checkpoints/
ls -la /workspace/ComfyUI/models/loras/
```

### If generation fails:
Check ComfyUI logs on your GPU instance for error messages.

## Next Steps After Success

Once your cloud GPU is connected:
1. **Deploy your app** using the FREE deployment guide
2. **Your web app** will run on Railway (free)
3. **Image processing** will use your cloud GPU
4. **Users worldwide** can access your Face Morphing SaaS

---

**Please provide your GPU instance IP address so I can help you configure the connection!**