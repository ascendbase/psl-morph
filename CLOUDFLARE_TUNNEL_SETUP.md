# Cloudflare Tunnel Setup Guide for Windows

This guide shows you how to install and set up Cloudflare Tunnel to expose your local ComfyUI to your Railway app.

## 🚀 Why Cloudflare Tunnel?

- **Free** - No cost for basic usage
- **Reliable** - Better uptime than ngrok free tier
- **Secure** - Built-in DDoS protection and HTTPS
- **Stable** - Doesn't change URLs like ngrok free tier
- **Fast** - Cloudflare's global network

## 📥 Installation Methods

### Method 1: Direct Download (Recommended)

1. **Download cloudflared**:
   - Go to: https://github.com/cloudflare/cloudflared/releases/latest
   - Download `cloudflared-windows-amd64.exe`
   - Rename it to `cloudflared.exe`

2. **Create a folder**:
   ```
   C:\cloudflared\
   ```

3. **Move the file**:
   - Move `cloudflared.exe` to `C:\cloudflared\`

4. **Add to PATH**:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\cloudflared`
   - Click "OK" on all dialogs

5. **Test installation**:
   - Open Command Prompt
   - Type: `cloudflared --version`
   - You should see version information

### Method 2: Using Chocolatey

If you have Chocolatey installed:

```powershell
choco install cloudflared
```

### Method 3: Using Scoop

If you have Scoop installed:

```powershell
scoop install cloudflared
```

## 🔧 Setup Cloudflare Tunnel

### Step 1: Login to Cloudflare

```bash
cloudflared tunnel login
```

This will:
- Open your browser
- Ask you to login to Cloudflare (create free account if needed)
- Authorize cloudflared to access your account

### Step 2: Create a Tunnel

```bash
cloudflared tunnel create comfyui-tunnel
```

This creates a tunnel named "comfyui-tunnel" and generates a tunnel ID.

### Step 3: Start the Tunnel (Quick Method)

For quick testing, use this simple command:

```bash
cloudflared tunnel --url http://localhost:8188
```

This will:
- Create a temporary tunnel
- Give you a public URL (e.g., `https://abc-def-ghi.trycloudflare.com`)
- Forward traffic to your local ComfyUI on port 8188

### Step 4: Start the Tunnel (Persistent Method)

For production use, create a configuration file:

1. **Create config file**:
   - Create folder: `C:\Users\%USERNAME%\.cloudflared\`
   - Create file: `config.yml`

2. **Add configuration**:
   ```yaml
   tunnel: comfyui-tunnel
   credentials-file: C:\Users\%USERNAME%\.cloudflared\[TUNNEL-ID].json
   
   ingress:
     - hostname: your-domain.com  # Optional: use your own domain
       service: http://localhost:8188
     - service: http_status:404
   ```

3. **Start tunnel**:
   ```bash
   cloudflared tunnel run comfyui-tunnel
   ```

## 🎯 Complete Setup Script

Create `setup_cloudflare_tunnel.bat`:

```batch
@echo off
echo ========================================
echo   CLOUDFLARE TUNNEL SETUP
echo ========================================
echo.

echo Step 1: Checking if cloudflared is installed...
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo cloudflared not found!
    echo Please install it first:
    echo 1. Download from: https://github.com/cloudflare/cloudflared/releases/latest
    echo 2. Download cloudflared-windows-amd64.exe
    echo 3. Rename to cloudflared.exe
    echo 4. Move to C:\cloudflared\
    echo 5. Add C:\cloudflared to your PATH
    echo.
    pause
    exit /b 1
)

echo cloudflared found!
cloudflared --version
echo.

echo Step 2: Login to Cloudflare (if not already logged in)...
echo This will open your browser for authentication
pause
cloudflared tunnel login

echo.
echo Step 3: Starting tunnel for ComfyUI...
echo This will create a public URL for your local ComfyUI
echo.

echo Starting tunnel on port 8188...
echo Keep this window open to maintain the tunnel!
echo.

cloudflared tunnel --url http://localhost:8188
```

## 🚀 Production Setup Script

Create `start_production_cloudflare.bat`:

```batch
@echo off
echo ========================================
echo   PRODUCTION CLOUDFLARE TUNNEL SETUP
echo ========================================
echo.

echo Step 1: Starting ComfyUI...
if exist "D:\ComfyUI_windows_portable" (
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && python main.py"
) else (
    echo ComfyUI not found at D:\ComfyUI_windows_portable
    set /p comfyui_path="Enter your ComfyUI path: "
    start "ComfyUI" cmd /k "cd /d %comfyui_path% && python main.py"
)

echo Waiting 15 seconds for ComfyUI to start...
timeout /t 15

echo.
echo Step 2: Starting Cloudflare Tunnel...
echo This will expose your ComfyUI to the internet securely
echo.

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8188"

echo.
echo Waiting 10 seconds for tunnel to start...
timeout /t 10

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Your local ComfyUI is now accessible to Railway!
echo.
echo Next steps:
echo 1. Check the Cloudflare Tunnel window for your public URL
echo 2. Copy the URL (e.g., https://abc-def-ghi.trycloudflare.com)
echo 3. Go to your Railway project dashboard
echo 4. Add these environment variables:
echo    - USE_LOCAL_COMFYUI=true
echo    - USE_MODAL=false
echo    - USE_CLOUD_GPU=false
echo    - LOCAL_COMFYUI_URL=https://your-cloudflare-url.trycloudflare.com
echo    - LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json
echo 5. Deploy your Railway app
echo 6. Test with users worldwide!
echo.
echo IMPORTANT: Keep both windows open to serve users
echo Close the tunnel window to stop serving.
echo.

pause
```

## 🔍 Troubleshooting

### Installation Issues

**Error: "cloudflared is not recognized"**
- Make sure you added `C:\cloudflared` to your PATH
- Restart Command Prompt after adding to PATH
- Check the file is named `cloudflared.exe` (not `cloudflared-windows-amd64.exe`)

**Error: "Access denied"**
- Run Command Prompt as Administrator
- Make sure you have write permissions to `C:\cloudflared`

### Tunnel Issues

**Error: "failed to login"**
- Make sure you have a Cloudflare account
- Check your internet connection
- Try running as Administrator

**Error: "tunnel already exists"**
- Use a different tunnel name
- Or delete the existing tunnel: `cloudflared tunnel delete comfyui-tunnel`

**Tunnel disconnects frequently**
- Check your internet connection stability
- Consider using the persistent method with config file
- Monitor for firewall/antivirus interference

## 🆚 Cloudflare vs ngrok Comparison

| Feature | Cloudflare Tunnel | ngrok |
|---------|------------------|-------|
| **Cost** | Free | Free (limited) |
| **URL Stability** | Stable | Changes on restart (free) |
| **Speed** | Very fast | Good |
| **Reliability** | Excellent | Good |
| **Setup** | Medium | Easy |
| **Security** | Excellent | Good |
| **Custom Domains** | Yes (free) | Paid only |

## 🎉 Success!

Once set up, your Cloudflare tunnel will:
1. Provide a stable public URL for your ComfyUI
2. Handle HTTPS automatically
3. Protect against DDoS attacks
4. Allow your Railway app to connect to your local GPU
5. Serve users worldwide with excellent performance

Your Railway app can now use your local ComfyUI through the secure Cloudflare tunnel! 🚀
