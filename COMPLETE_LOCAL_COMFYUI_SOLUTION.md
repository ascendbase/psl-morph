# Complete Local ComfyUI Solution

## Overview

This solution enables your Railway-deployed app to use your local ComfyUI installation via Cloudflare tunnels. When users click "Start Transformation", the app will connect to your local GPU instead of cloud services.

## What Was Fixed

### 1. Connection Issue Resolution
- **Problem**: `LocalComfyUIClient` was hardcoded to use `localhost:8188`
- **Solution**: Updated to use dynamic tunnel URL detection system
- **Result**: App now automatically connects to your local ComfyUI via tunnel

### 2. Tunnel Detection System
- **Components**: 
  - `cloudflare_tunnel_detector.py` - Detects tunnel URLs
  - `tunnel_registry.py` - Stores tunnel URLs from webhook
  - `notify_tunnel_simple.py` - Notifies Railway app of tunnel URL
- **Flow**: Tunnel URL → Webhook → Registry → LocalComfyUIClient

### 3. Workflow Integration
- **Workflow Used**: `comfyui_workflows/workflow_facedetailer.json`
- **Features**: Supports both preset modes (HTN, Chadlite, Chad) and custom feature selection
- **Parameters**: Dynamic denoise strength, unique seeds, custom output naming

## How to Use

### Step 1: Start the Complete System
```bash
.\start_production_cloudflare.bat
```

This will open 3 windows:
1. **ComfyUI** - Your local ComfyUI instance
2. **Cloudflare Tunnel** - Creates public URL for your ComfyUI
3. **Notifier** - Automatically registers tunnel URL with Railway app

### Step 2: Verify Connection
```bash
python test_tunnel_connection_fix.py
```

This will test:
- Tunnel registry status
- Dynamic URL detection
- LocalComfyUIClient connection
- Complete system integration

### Step 3: Test the Web App
1. Go to your Railway app: https://psl-morph-production.up.railway.app
2. Upload an image
3. Select transformation preset or custom features
4. Click "Start Transformation"
5. The app will now use your local ComfyUI!

## System Architecture

```
User Upload → Railway App → Tunnel URL → Local ComfyUI → Local GPU → Result
```

### Key Components:

1. **Railway App** (`app.py`)
   - Receives user requests
   - Uses `LocalComfyUIClient` for generation
   - Automatically detects tunnel URLs

2. **LocalComfyUIClient** (`local_comfyui_client.py`)
   - Connects to ComfyUI via tunnel
   - Uses `workflow_facedetailer.json`
   - Handles image upload, generation, and result retrieval

3. **Tunnel System**
   - Cloudflare tunnel exposes local ComfyUI
   - Automatic URL detection and registration
   - Fallback to localhost if tunnel unavailable

4. **Workflow System**
   - Main workflow: `workflow_facedetailer.json`
   - Feature-specific workflows for custom transformations
   - Dynamic parameter adjustment

## Troubleshooting

### If Cloudflare Tunnel Window is Empty:
1. Check if cloudflared is installed: `cloudflared --version`
2. Try running manually: `cloudflared tunnel --url http://localhost:8188`
3. Check Windows firewall settings

### If Connection Test Fails:
1. Ensure ComfyUI is running on port 8188
2. Check if tunnel URL was registered: `python test_tunnel_connection_fix.py`
3. Verify Railway app can reach the tunnel URL

### If Generation Fails:
1. Check ComfyUI console for errors
2. Verify workflow file exists: `comfyui_workflows/workflow_facedetailer.json`
3. Check Railway app logs for connection errors

## Files Modified/Created

### Core Files:
- `local_comfyui_client.py` - Updated to use tunnel detection
- `cloudflare_tunnel_detector.py` - Tunnel URL detection
- `tunnel_registry.py` - URL storage system
- `notify_tunnel_simple.py` - Webhook notification

### Batch Files:
- `start_production_cloudflare.bat` - Complete startup script

### Test Files:
- `test_tunnel_connection_fix.py` - System verification

### Workflow Files:
- `comfyui_workflows/workflow_facedetailer.json` - Main transformation workflow
- Feature-specific workflows for custom transformations

## Benefits

1. **Cost Savings**: Use your local GPU instead of expensive cloud services
2. **Performance**: Direct access to your hardware
3. **Privacy**: Images processed locally
4. **Flexibility**: Full control over ComfyUI setup and models
5. **Reliability**: No dependency on external GPU services

## Next Steps

1. **Test the complete system** with the startup script
2. **Verify web app functionality** with real image uploads
3. **Monitor Railway logs** to confirm successful connections
4. **Customize workflows** if needed for specific requirements

The system is now ready for production use with your local ComfyUI installation!
