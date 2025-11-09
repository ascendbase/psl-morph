# Complete Local ComfyUI Integration Guide

## 🎯 Overview

Your Railway app can now seamlessly connect to your local ComfyUI instance using Cloudflare tunnels. When users click "Start Transformation", the Railway app will automatically use your local GPU for processing.

## 🔧 What Was Fixed

### 1. App Integration
- ✅ Updated `app.py` to use registered tunnel URLs
- ✅ Added global tunnel URL storage
- ✅ Enhanced `/register-tunnel` endpoint with better validation
- ✅ Automatic GPU client URL updates when tunnel is registered

### 2. Tunnel Detection
- ✅ Updated `cloudflare_tunnel_detector.py` to prioritize registered URLs
- ✅ Added fallback mechanisms for tunnel detection
- ✅ Improved connection testing and validation

### 3. Workflow Integration
- ✅ App uses `workflow_facedetailer.json` from your ComfyUI workflows
- ✅ Automatic parameter mapping for different transformation tiers
- ✅ Real-time tunnel URL updates

## 🚀 How to Use

### Step 1: Deploy Updated App to Railway
```bash
railway up
```

### Step 2: Start Local ComfyUI
1. Start your ComfyUI instance on port 8188
2. Make sure the FaceDetailer workflow is loaded
3. Ensure all required models are installed

### Step 3: Start Cloudflare Tunnel
Run the production script:
```bash
start_production_cloudflare.bat
```

This will:
- Start Cloudflare tunnel
- Auto-detect the tunnel URL
- Register it with your Railway app
- Update the app to use your local GPU

### Step 4: Test the Integration
1. Go to your Railway app URL
2. Upload an image
3. Click "Start Transformation"
4. The app will use your local ComfyUI for processing!

## 🔍 How It Works

### Tunnel Registration Flow
1. `start_production_cloudflare.bat` starts Cloudflare tunnel
2. Script detects the tunnel URL from logs
3. Sends POST request to Railway app's `/register-tunnel` endpoint
4. Railway app validates the URL and stores it globally
5. App updates the GPU client to use the new tunnel URL

### Processing Flow
1. User uploads image and clicks "Start Transformation"
2. App checks for registered tunnel URL first
3. If found, uses tunnel URL for ComfyUI processing
4. Falls back to local detection if tunnel URL unavailable
5. Processes image using your local GPU via tunnel

## 📋 Environment Variables

Make sure these are set in Railway:

```env
USE_LOCAL_COMFYUI=true
LOCAL_COMFYUI_URL=http://127.0.0.1:8188
LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json
REGISTER_TUNNEL_SECRET=morphpas
```

## 🔧 Troubleshooting

### Tunnel Not Connecting
1. Check if ComfyUI is running on port 8188
2. Verify Cloudflare tunnel is active
3. Check Railway logs for tunnel registration messages
4. Test tunnel URL manually: `https://your-tunnel.trycloudflare.com/system_stats`

### App Not Using Local GPU
1. Check Railway logs for "✅ Registered tunnel URL" message
2. Verify `/register-tunnel` endpoint received the URL
3. Test the `/gpu-status` endpoint on your Railway app
4. Restart the tunnel registration if needed

### Processing Errors
1. Ensure FaceDetailer workflow is properly loaded in ComfyUI
2. Check that all required models are installed
3. Verify workflow file `workflow_facedetailer.json` exists
4. Check ComfyUI console for error messages

## 📊 Monitoring

### Check Tunnel Status
Visit your Railway app's `/health` endpoint to see:
- GPU connection status
- Tunnel URL being used
- ComfyUI version and devices

### Check GPU Status
Visit `/gpu-status` endpoint for real-time GPU availability.

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ Railway logs show "✅ Registered tunnel URL via webhook"
2. ✅ Railway logs show "🔄 Updated Local ComfyUI client to use"
3. ✅ `/health` endpoint shows "local_comfyui" as GPU type
4. ✅ Image processing completes using your local GPU
5. ✅ No cloud GPU costs incurred!

## 💡 Benefits

- **Zero Cloud GPU Costs**: Use your own hardware
- **Full Control**: Your models, your settings
- **High Performance**: Direct access to your GPU
- **Privacy**: Images processed locally
- **Flexibility**: Easy to modify workflows

## 🔄 Workflow Customization

To use different workflows:
1. Place your workflow JSON in `comfyui_workflows/`
2. Update `LOCAL_COMFYUI_WORKFLOW` in Railway environment
3. Redeploy the app
4. The app will automatically use your custom workflow

## 📝 Notes

- The tunnel URL is automatically detected and registered
- Railway app prioritizes registered tunnel URLs over auto-detection
- Tunnel registration includes connectivity validation
- App gracefully falls back to local URLs if tunnel fails
- All existing cloud GPU fallbacks remain intact

Your Railway app is now fully integrated with your local ComfyUI setup! 🚀
