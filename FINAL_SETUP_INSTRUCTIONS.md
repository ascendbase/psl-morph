# Final Setup: Connect Your RTX 5090 to Face Morphing App

## Current Status ✅
- ComfyUI is running on your RTX 5090 pod
- Your Face Morphing SaaS app is ready
- Only need SSH tunnel to connect them

## Simple 2-Step Setup

### Step 1: Create SSH Tunnel
You have 3 options:

#### Option A: Use Password (if available)
Check your RunPod dashboard for root password, then:
```bash
ssh root@149.36.1.79 -p 33805 -L 8188:localhost:8188 -N
```

#### Option B: Use SSH Key (recommended)
1. Download SSH key from RunPod dashboard → save as `C:\Users\yvngt\.ssh\id_ed25519`
2. Run:
```bash
ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N
```

#### Option C: Use Batch File
Double-click [`fix_ssh_key.bat`](fix_ssh_key.bat) for automated setup.

### Step 2: Run Your App
In a new terminal:
```bash
python app.py
```

## Test Everything Works

1. **Test SSH Tunnel**: Visit http://localhost:8188 (should show ComfyUI)
2. **Test Your App**: Visit http://localhost:5000 (your Face Morphing app)
3. **Test Face Morphing**: Upload image, select HTN/Chadlite/Chad, generate!

## What Happens
- SSH tunnel: `localhost:8188` → your RTX 5090 ComfyUI
- Your app connects to `localhost:8188` 
- Face morphing uses your RTX 5090 (32GB VRAM!)
- Users can buy credits and generate images
- Admin panel manages everything

## Troubleshooting
- **SSH fails**: Try password method or re-download SSH key
- **App can't connect**: Make sure SSH tunnel is running
- **Generation fails**: Check ComfyUI is running on pod

## Your Complete SaaS Platform
- ✅ User authentication & registration
- ✅ Credit system (free + paid tiers)
- ✅ Payment processing (crypto + bank transfer)
- ✅ RTX 5090 cloud GPU processing
- ✅ Admin panel for user management
- ✅ Face morphing with 3 intensity levels

Ready to launch! 🚀