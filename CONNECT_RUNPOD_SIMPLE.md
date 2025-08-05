# How to Connect Your RunPod GPU to Your Face Morphing App

## The Problem
- Your RTX 5090 is running ComfyUI ✅
- Your Face Morphing app is ready ✅
- They can't talk to each other ❌

## The Solution (3 Simple Steps)

### Step 1: Get Your RunPod Password
1. Go to your RunPod dashboard
2. Look for "Root Password" or "Password" 
3. Copy the password

### Step 2: Create the Connection Bridge
Open a new terminal and run this command:
```bash
ssh root@149.36.1.79 -p 33805 -L 8188:localhost:8188 -N
```

When it asks for password, paste the password from Step 1.

**Keep this terminal open!** This creates a "bridge" so your app can reach your GPU.

### Step 3: Test the Bridge
Open your web browser and go to: http://localhost:8188

If you see the ComfyUI interface, the bridge works! ✅

### Step 4: Run Your App
Open another terminal and run:
```bash
python app.py
```

Go to: http://localhost:5000

## What This Does
```
Your App (localhost:5000) 
    ↓
SSH Bridge (localhost:8188)
    ↓
Your RTX 5090 GPU (149.36.1.79)
```

## If It Doesn't Work
1. **Can't find password?** Look in RunPod dashboard under "Connection Details"
2. **SSH fails?** Try the RunPod web terminal instead (browser-based)
3. **Bridge doesn't work?** Make sure ComfyUI is still running on your pod

## Alternative: Use RunPod Web Terminal
If SSH is too complicated:
1. Use RunPod's web terminal (click "Terminal" in your pod dashboard)
2. ComfyUI is already running there
3. Look for any "Public URL" or "HTTP Endpoint" in your pod settings

The goal is simple: make localhost:8188 show ComfyUI, then your app will work!