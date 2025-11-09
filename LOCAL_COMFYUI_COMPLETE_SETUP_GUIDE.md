# 🚀 Complete Local ComfyUI Setup Guide

This guide will help you connect your Railway-deployed app to your local ComfyUI installation, allowing you to use your local GPU for image generation while keeping the web interface on Railway.

## 📋 Prerequisites

- ComfyUI installed locally
- Cloudflare tunnel (`cloudflared`) installed
- Your Railway app deployed at: https://psl-morph-production.up.railway.app
- Admin access to your Railway app

## 🔧 Step 1: Install Cloudflare Tunnel

### Windows:
```bash
# Download and install cloudflared
winget install --id Cloudflare.cloudflared
```

### Alternative Windows Installation:
1. Download from: https://github.com/cloudflare/cloudflared/releases
2. Extract `cloudflared.exe` to a folder in your PATH

### Linux/Mac:
```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Mac
brew install cloudflared
```

## 🎯 Step 2: Prepare ComfyUI

1. **Navigate to your ComfyUI directory**
2. **Start ComfyUI with network access:**
   ```bash
   python main.py --listen 0.0.0.0 --port 8188
   ```

3. **Verify ComfyUI is running:**
   - Open http://localhost:8188 in your browser
   - You should see the ComfyUI interface

## 🌐 Step 3: Create Cloudflare Tunnel

1. **Open a new terminal/command prompt**
2. **Start the tunnel:**
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8188
   ```

3. **Copy the tunnel URL:**
   - Look for output like: `https://abc-def-ghi.trycloudflare.com`
   - Copy this entire URL

## 🔗 Step 4: Register Tunnel with Railway App

### Method 1: Using the Registration Script
```bash
python register_tunnel_manual.py https://your-tunnel-url.trycloudflare.com
```

### Method 2: Using Admin Dashboard
1. Go to: https://psl-morph-production.up.railway.app/admin
2. Click on "🖥️ GPU Settings" tab
3. Paste your tunnel URL in the "Cloudflare Tunnel URL" field
4. Click "💾 Set Tunnel URL"
5. Click "🧪 Test Connection" to verify

### Method 3: Manual API Call
```bash
curl -X POST https://psl-morph-production.up.railway.app/register-tunnel \
  -H "Content-Type: application/json" \
  -H "X-TUNNEL-SECRET: morphpas" \
  -d '{"url": "https://your-tunnel-url.trycloudflare.com"}'
```

## ✅ Step 5: Verify Setup

1. **Check GPU Status:**
   - Go to: https://psl-morph-production.up.railway.app/app
   - Look for green "✅ GPU Available" status

2. **Test Image Generation:**
   - Upload an image
   - Click "🚀 Start Transformation"
   - Monitor the process

## 🔄 Step 6: Workflow Setup

Your app will now use the workflow file: `D:\Morph-app\comfyui_workflows\workflow_facedetailer.json`

Make sure this file exists and contains a valid ComfyUI workflow.

## 🛠️ Troubleshooting

### Issue: "GPU Unavailable" Status
**Solutions:**
1. Check ComfyUI is running: http://localhost:8188
2. Verify tunnel is active and accessible
3. Re-register the tunnel URL
4. Check firewall settings

### Issue: Tunnel Connection Failed
**Solutions:**
1. Restart ComfyUI
2. Restart the tunnel with a new URL
3. Check Windows Firewall/antivirus
4. Try different tunnel command:
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8188 --protocol http2
   ```

### Issue: "CORS" or "Network" Errors
**Solutions:**
1. Ensure ComfyUI started with `--listen 0.0.0.0`
2. Check if port 8188 is available
3. Try restarting both ComfyUI and tunnel

### Issue: Slow Generation
**Solutions:**
1. Check your GPU utilization
2. Ensure no other processes are using GPU
3. Monitor ComfyUI console for errors

## 📱 Daily Usage Workflow

1. **Start ComfyUI:**
   ```bash
   cd /path/to/ComfyUI
   python main.py --listen 0.0.0.0 --port 8188
   ```

2. **Start Tunnel (new terminal):**
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8188
   ```

3. **Register Tunnel:**
   ```bash
   python register_tunnel_manual.py https://new-tunnel-url.trycloudflare.com
   ```

4. **Use the App:**
   - Go to: https://psl-morph-production.up.railway.app/app
   - Generate images using your local GPU!

## 🔒 Security Notes

- The tunnel is temporary and changes each time you restart it
- Only your Railway app can access the tunnel (protected by secret)
- ComfyUI is only accessible through the tunnel, not directly
- No permanent firewall changes needed

## 💡 Pro Tips

1. **Keep terminals open:** Don't close ComfyUI or tunnel terminals
2. **Monitor logs:** Watch ComfyUI console for generation progress
3. **GPU monitoring:** Use Task Manager or `nvidia-smi` to monitor GPU usage
4. **Backup workflows:** Keep your workflow files backed up
5. **Test locally first:** Always test workflows in ComfyUI before using via tunnel

## 🎉 Success Indicators

- ✅ ComfyUI accessible at http://localhost:8188
- ✅ Tunnel shows "Connection established" message
- ✅ Railway app shows "GPU Available" status
- ✅ Test image generation completes successfully
- ✅ Generated images download properly

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all steps were followed correctly
3. Check ComfyUI and tunnel logs for errors
4. Ensure your GPU drivers are up to date

---

**🎯 Goal Achieved:** Your Railway app now uses your local GPU for image generation while maintaining the professional web interface and user management system!
