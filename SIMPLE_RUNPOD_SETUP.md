# Simple RunPod Connection Guide

Based on your RunPod dashboard, here's the easiest way to connect:

## Step 1: Get Your SSH Key
1. In your RunPod dashboard, look for "SSH Key" or "Download Key"
2. Download the `id_ed25519` file
3. Save it to: `C:\Users\yvngt\.ssh\id_ed25519`

## Step 2: Fix Key Permissions (Windows)
Open PowerShell as Administrator and run:
```powershell
# Create .ssh folder if it doesn't exist
mkdir C:\Users\yvngt\.ssh -Force

# Set correct permissions
icacls C:\Users\yvngt\.ssh\id_ed25519 /inheritance:r
icacls C:\Users\yvngt\.ssh\id_ed25519 /grant:r yvngt:R
```

## Step 3: Connect with SSH Tunnel
Use the exact command from your RunPod dashboard but add the tunnel:
```bash
ssh root@149.36.1.79 -p 33805 -i ~/.ssh/id_ed25519 -L 8188:localhost:8188 -N
```

## Step 4: Test Connection
1. Keep the SSH tunnel running
2. Open browser: http://localhost:8188
3. You should see ComfyUI interface

## Step 5: Run Your App
```bash
python app.py
```

## Alternative: Use RunPod Web Terminal
If SSH is still problematic:
1. Use RunPod's web terminal (browser-based)
2. Start ComfyUI: `python main.py --listen 0.0.0.0 --port 8188`
3. Use RunPod's HTTP proxy URL (if available)

## Troubleshooting
- **Key not working**: Make sure the key file has no extension (.txt, etc.)
- **Permission denied**: Run the PowerShell commands as Administrator
- **Connection refused**: Make sure your RunPod is running and ComfyUI is started

The key is using the exact SSH key file that RunPod provides, not typing passwords.