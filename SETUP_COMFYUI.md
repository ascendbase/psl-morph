# ComfyUI API Setup Guide

This guide will help you set up ComfyUI with API access for the Face Morphing Web App.

## 📋 Prerequisites

- ComfyUI installed and working
- ReActor extension installed
- Your custom LoRA model (`chad_sd1.5.safetensors`)
- Base model (`real-dream-15.safetensors`)

## 🚀 Step-by-Step Setup

### 1. Install Required ComfyUI Extensions

#### ReActor Face Swap Extension
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Gourieff/comfyui-reactor-node.git
cd comfyui-reactor-node
pip install -r requirements.txt
```

### 2. Organize Your Models

Place your models in the correct ComfyUI directories:

```
ComfyUI/
├── models/
│   ├── checkpoints/
│   │   └── real-dream-15.safetensors
│   ├── loras/
│   │   └── chad_sd1.5.safetensors
│   └── insightface/
│       └── inswapper_128.onnx  # ReActor model
```

### 3. Start ComfyUI with API Enabled

#### Option A: Local Access Only
```bash
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

#### Option B: Network Access (for remote web app)
```bash
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

#### Option C: With Additional Options
```bash
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header
```

### 4. Verify API is Working

Open your browser and visit:
- http://127.0.0.1:8188 - ComfyUI Web Interface
- http://127.0.0.1:8188/system_stats - API Health Check

You should see JSON response for the system stats endpoint.

### 5. Test Your Workflow

1. Open ComfyUI web interface
2. Load your workflow from `comfyui_workflows/workflow.json`
3. Upload a test image
4. Run the workflow manually to ensure it works
5. Check that all nodes load correctly (no red nodes)

## 🔧 Troubleshooting

### Common Issues

#### 1. ReActor Extension Not Loading
```bash
# Reinstall ReActor dependencies
cd ComfyUI/custom_nodes/comfyui-reactor-node
pip install -r requirements.txt --upgrade
```

#### 2. Missing Models
- Download `inswapper_128.onnx` from ReActor releases
- Place in `ComfyUI/models/insightface/`
- Ensure your LoRA and checkpoint files are in correct directories

#### 3. API Not Accessible
- Check firewall settings
- Verify ComfyUI started with `--listen` parameter
- Test with curl: `curl http://127.0.0.1:8188/system_stats`

#### 4. CORS Issues (for web deployment)
```bash
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

### 5. Memory Issues
```bash
# For low VRAM systems
python main.py --lowvram --listen 127.0.0.1 --port 8188

# For very low VRAM systems
python main.py --cpu --listen 127.0.0.1 --port 8188
```

## 📝 Configuration Files

### ComfyUI Startup Script (Windows)
Create `start_comfyui.bat`:
```batch
@echo off
cd /d "C:\path\to\ComfyUI"
python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header
pause
```

### ComfyUI Startup Script (Linux/Mac)
Create `start_comfyui.sh`:
```bash
#!/bin/bash
cd /path/to/ComfyUI
python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header
```

## 🔒 Security Considerations

### For Local Use
- Use `--listen 127.0.0.1` to restrict access to localhost only
- No additional security needed for local development

### For Network/Production Use
- Consider using reverse proxy (nginx) with authentication
- Use HTTPS in production
- Implement rate limiting
- Monitor resource usage

## 🧪 Testing the Integration

### Manual API Test
```bash
# Test system stats
curl http://127.0.0.1:8188/system_stats

# Test workflow queue (replace with your workflow JSON)
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": {...}, "client_id": "test"}'
```

### Using the Web App Health Check
1. Start ComfyUI with API enabled
2. Start the Face Morphing Web App
3. Visit http://localhost:5000/health
4. Should show `"comfyui": "connected"`

## 📊 Performance Optimization

### GPU Optimization
- Ensure CUDA is properly installed
- Use appropriate `--gpu-only` flags if needed
- Monitor GPU memory usage

### CPU Optimization
- Use `--threads` parameter to control CPU usage
- Consider `--highvram` for systems with lots of RAM

### Storage Optimization
- Regularly clean ComfyUI output directory
- Use SSD for model storage if possible
- Consider model quantization for faster loading

## 🔄 Workflow Customization

### Modifying the Workflow
1. Open ComfyUI web interface
2. Load and modify your workflow
3. Export as JSON
4. Replace `comfyui_workflows/workflow.json`
5. Update node parameters in web app if needed

### Adding New Presets
1. Modify `config.py` PRESETS dictionary
2. Add new denoise values and descriptions
3. Update frontend if needed

## 📞 Support

If you encounter issues:
1. Check ComfyUI console for error messages
2. Verify all models are properly loaded
3. Test workflow manually in ComfyUI first
4. Check web app logs for API communication errors

---

**Next Step**: Once ComfyUI API is running, start the Face Morphing Web App with `python app.py`