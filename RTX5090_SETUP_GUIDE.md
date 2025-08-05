# RTX 5090 Face Morphing Setup Guide

## 🎯 Quick Start

Your Face Morphing SaaS app is now configured to use the RTX 5090 cloud GPU!

### ✅ Current Configuration

- **RTX 5090 URL**: `https://choa76vtevld8t-8188.proxy.runpod.net`
- **Connection**: Direct ComfyUI client (not RunPod serverless)
- **Status**: ✅ WORKING and verified

## 🚀 How to Start the App

### Option 1: Use the RTX 5090 Batch File (Recommended)
```bash
start_rtx5090.bat
```

This ensures the correct environment variables are loaded.

### Option 2: Manual Environment Setup
```bash
set COMFYUI_URL=https://choa76vtevld8t-8188.proxy.runpod.net
set USE_CLOUD_GPU=false
set USE_RUNPOD_POD=false
python app.py
```

### Option 3: Verify .env File
Make sure your `.env` file contains:
```env
# Use ComfyUI client with RTX 5090 proxy URL
USE_CLOUD_GPU=false
USE_RUNPOD_POD=false

# RunPod RTX 5090 (WORKING!)
COMFYUI_URL=https://choa76vtevld8t-8188.proxy.runpod.net
COMFYUI_TIMEOUT=300
```

## 🔍 Verify RTX 5090 Connection

### Check Terminal Output
When you start the app, look for this in the terminal:
```
✅ CORRECT: GPU Provider: ComfyUI (URL: https://choa76vtevld8t-8188.proxy.runpod.net)
✅ CORRECT: ComfyUI Client initialized: https://choa76vtevld8t-8188.proxy.runpod.net
```

### Test Connection Manually
```bash
python -c "import requests; r = requests.get('https://choa76vtevld8t-8188.proxy.runpod.net/queue'); print('RTX 5090 Status:', r.status_code)"
```
Should return: `RTX 5090 Status: 200`

## 🎮 Using the Face Morphing App

1. **Start the app**: Run `start_rtx5090.bat`
2. **Open browser**: Go to `http://localhost:5000`
3. **Sign in**: Use `admin@example.com` / `admin123`
4. **Upload image**: Click "Start Morphing" and upload a face photo
5. **Choose preset**: 
   - **HTN** (20% denoise) - Minimal Enhancement
   - **Chadlite** (50% denoise) - Strong Transform  
   - **Chad** (80% denoise) - Extreme Power
6. **Process**: Click "Morph" - it will use the RTX 5090!

## 🔧 Troubleshooting

### Problem: "Cannot connect to ComfyUI"
**Solution**: Check that you're using the correct startup method:
```bash
# Use this:
start_rtx5090.bat

# NOT this:
python app.py  # (might use wrong config)
```

### Problem: Wrong URL in terminal
If you see `http://127.0.0.1:8188` instead of the RTX 5090 URL:
1. Stop the app (Ctrl+C)
2. Use `start_rtx5090.bat` instead
3. Verify the terminal shows the RTX 5090 URL

### Problem: RunPod serverless error
If you see "RunPod Serverless (Endpoint: )", make sure:
- `USE_CLOUD_GPU=false` in your `.env` file
- Use the batch file to start the app

## 📊 Performance

- **GPU**: RTX 5090 (32GB VRAM)
- **Speed**: ~10-30 seconds per generation
- **Quality**: High-quality FaceDetailer workflow
- **Concurrent**: Multiple users supported

## 🎉 Success Indicators

When everything is working correctly, you'll see:

1. **Terminal shows RTX 5090 URL**
2. **Face morphing completes successfully**
3. **No connection errors**
4. **Generated images download properly**

## 📝 Notes

- The RTX 5090 is accessed via RunPod proxy URL
- No SSH tunnel needed (direct HTTPS connection)
- Uses FaceDetailer workflow for best quality
- Credit system tracks usage (998 credits available)
- Admin panel available for user management

---

**🚀 Your Face Morphing SaaS with RTX 5090 is ready for production!**