# Railway to Local ComfyUI Integration Guide

This guide shows you how to make your Railway-deployed web app call your local ComfyUI for processing, allowing users worldwide to use your local GPU.

## 🎯 What We're Achieving

- **Railway Web App** (accessible worldwide) → **Your Local ComfyUI** (your GPU)
- Users upload images to Railway → Railway sends to your local ComfyUI → Your GPU processes → Result sent back to users
- **Zero cloud GPU costs** while serving users globally!

## 🔧 Setup Steps

### Step 1: Expose Your Local ComfyUI to the Internet

You need to make your local ComfyUI accessible from the internet so Railway can reach it. Here are the best options:

#### Option A: ngrok (Recommended - Easy & Secure)

1. **Download ngrok**: https://ngrok.com/download
2. **Sign up** for a free ngrok account
3. **Install ngrok** and authenticate:
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```
4. **Start ComfyUI** on your local machine (default port 8188)
5. **Expose ComfyUI** with ngrok:
   ```bash
   ngrok http 8188
   ```
6. **Copy the public URL** (e.g., `https://abc123.ngrok.io`)

#### Option B: Cloudflare Tunnel (Free & Reliable)

1. **Install Cloudflare Tunnel**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
2. **Login to Cloudflare**:
   ```bash
   cloudflared tunnel login
   ```
3. **Create a tunnel**:
   ```bash
   cloudflared tunnel create comfyui-tunnel
   ```
4. **Start the tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:8188
   ```
5. **Copy the public URL** provided

#### Option C: Port Forwarding (Advanced)

1. **Configure your router** to forward port 8188 to your computer
2. **Find your public IP**: https://whatismyipaddress.com/
3. **Your public URL** will be: `http://YOUR_PUBLIC_IP:8188`
4. **Note**: This exposes your ComfyUI to the entire internet - use with caution!

### Step 2: Configure Railway Environment Variables

In your Railway project dashboard:

1. Go to **Variables** tab
2. Add these environment variables:
   ```
   USE_LOCAL_COMFYUI=true
   USE_MODAL=false
   USE_CLOUD_GPU=false
   LOCAL_COMFYUI_URL=https://your-ngrok-url.ngrok.io
   LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json
   ```

Replace `https://your-ngrok-url.ngrok.io` with your actual public URL from Step 1.

### Step 3: Deploy to Railway

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add local ComfyUI integration"
   git push origin main
   ```

2. **Railway will auto-deploy** your updated app

### Step 4: Test the Integration

1. **Start your local ComfyUI** with required models:
   - `real-dream-15.safetensors` (checkpoint)
   - `chad_sd1.5.safetensors` (LoRA)
   - FaceDetailer nodes installed

2. **Start your tunnel** (ngrok/Cloudflare)

3. **Visit your Railway app** and test image generation

4. **Monitor logs** in Railway dashboard to see the connection to your local ComfyUI

## 🔒 Security Considerations

### ngrok Security (Recommended)
- ✅ HTTPS encryption
- ✅ Authentication tokens
- ✅ Temporary URLs that change
- ✅ Built-in access controls

### Cloudflare Tunnel Security
- ✅ HTTPS encryption
- ✅ DDoS protection
- ✅ Access controls available
- ✅ Reliable infrastructure

### Port Forwarding Security
- ⚠️ Exposes ComfyUI to entire internet
- ⚠️ No built-in authentication
- ⚠️ Potential security risks
- ⚠️ Only use if you understand the risks

## 📊 Performance & Costs

### Benefits:
- **$0 cloud GPU costs** - Use your own hardware
- **Full control** over models and settings
- **No usage limits** - Generate as much as you want
- **Privacy** - Images processed on your hardware
- **Custom models** - Use any models you have

### Considerations:
- **Internet speed** affects upload/download times
- **Uptime** depends on your computer being on
- **Power costs** from running your GPU
- **Bandwidth usage** for image transfers

## 🛠️ Troubleshooting

### Railway Can't Connect to Local ComfyUI

1. **Check tunnel status**:
   - Ensure ngrok/Cloudflare tunnel is running
   - Verify the public URL is accessible from browser

2. **Check ComfyUI status**:
   - Ensure ComfyUI is running on port 8188
   - Test locally: http://localhost:8188

3. **Check Railway environment variables**:
   - Verify `LOCAL_COMFYUI_URL` is correct
   - Ensure `USE_LOCAL_COMFYUI=true`

4. **Check Railway logs**:
   - Look for connection errors
   - Check if the URL is being used correctly

### Slow Performance

1. **Optimize internet connection**:
   - Use wired connection instead of WiFi
   - Ensure good upload speed for image transfers

2. **Optimize ComfyUI**:
   - Use faster models if needed
   - Reduce image resolution if acceptable
   - Enable GPU optimizations

### Tunnel Disconnections

1. **ngrok**:
   - Use paid plan for stable URLs
   - Set up automatic restart scripts

2. **Cloudflare**:
   - Generally more stable than ngrok
   - Consider using a custom domain

## 🚀 Production Setup

For a production setup serving many users:

### 1. Stable URL
- Use ngrok paid plan or Cloudflare with custom domain
- Set up automatic tunnel restart

### 2. Monitoring
- Monitor your GPU temperature and usage
- Set up alerts for tunnel disconnections
- Monitor Railway app logs

### 3. Scaling
- Consider multiple GPUs if needed
- Load balancing between multiple ComfyUI instances
- Queue management for high traffic

### 4. Backup Plan
- Keep cloud GPU options as fallback
- Automatic failover if local GPU is unavailable

## 📝 Example Setup Script

Create `start_production_local.bat`:

```batch
@echo off
echo Starting Production Local ComfyUI Setup
echo =====================================

echo 1. Starting ComfyUI...
start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && python main.py"

timeout /t 10

echo 2. Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok http 8188"

echo 3. Setup complete!
echo - ComfyUI running on localhost:8188
echo - ngrok tunnel exposing to internet
echo - Update Railway environment variables with ngrok URL
echo - Your Railway app can now use your local GPU!

pause
```

## 🎉 Success!

Once set up, your Railway app will:
1. Accept image uploads from users worldwide
2. Send processing requests to your local ComfyUI
3. Use your local GPU for face transformations
4. Return results to users globally

You've successfully created a **global web app powered by your local GPU**! 🚀

## 💡 Pro Tips

1. **Keep ComfyUI updated** with latest models and nodes
2. **Monitor GPU temperature** during heavy usage
3. **Use SSD storage** for faster model loading
4. **Consider UPS** to prevent interruptions during processing
5. **Set up automatic restarts** for ComfyUI and tunnels
