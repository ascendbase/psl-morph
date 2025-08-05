# RunPod RTX 5090 Connection Fix Guide

## Problem
ComfyUI is running on your RunPod but the connection test fails because port 8188 is not exposed to the external network.

## Solution Steps

### 1. Check RunPod Port Configuration
Your RunPod needs to have port 8188 exposed. In your RunPod dashboard:
- Go to your pod settings
- Check "Exposed Ports" section
- Make sure port 8188 is listed and mapped

### 2. Alternative: Use RunPod's Public URL
RunPod provides a public URL for accessing services. Check your pod dashboard for:
- Public IP with port mapping
- Or a direct URL like: `https://your-pod-id-8188.proxy.runpod.net`

### 3. Fix ComfyUI Startup (if needed)
If ComfyUI is not accessible, restart it with proper network binding:

```bash
# Connect to your pod terminal
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

### 4. Test Connection Methods

#### Method A: Direct IP (if port is exposed)
```bash
curl http://149.36.1.79:8188/system_stats
```

#### Method B: RunPod Proxy URL
```bash
curl https://your-pod-id-8188.proxy.runpod.net/system_stats
```

### 5. Update Your .env File
Based on which method works, update your `.env`:

#### For Direct IP:
```env
RUNPOD_POD_URL=149.36.1.79
RUNPOD_POD_PORT=8188
```

#### For Proxy URL:
```env
RUNPOD_POD_URL=your-pod-id-8188.proxy.runpod.net
RUNPOD_POD_PORT=443
```

## Quick Fix Commands

### Install Missing Dependencies (for Impact Pack)
```bash
# On your RunPod terminal:
pip install opencv-python
pip install ultralytics
```

### Restart ComfyUI with CORS
```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

## Testing
After making changes, test the connection:
```bash
python test_runpod_pod.py
```

## Common Issues

1. **Port not exposed**: Check RunPod dashboard for port mapping
2. **Firewall blocking**: Use RunPod's proxy URL instead
3. **ComfyUI not binding to 0.0.0.0**: Restart with --listen 0.0.0.0
4. **CORS issues**: Add --enable-cors-header flag

## Next Steps
Once connection is working:
1. Upload your models to `/workspace/ComfyUI/models/`
2. Test face morphing workflow
3. Run the full app with `python app.py`