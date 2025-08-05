# Alternative: Use RunPod Web Terminal + HTTP Proxy

Since SSH key authentication is having issues, here are 2 easier alternatives:

## Option 1: RunPod Web Terminal (Easiest)

1. **Access Web Terminal**
   - Go to your RunPod dashboard
   - Click on your pod
   - Look for "Web Terminal" or "Terminal" button
   - This opens a browser-based terminal

2. **Start ComfyUI with External Access**
   ```bash
   cd /workspace/ComfyUI
   python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
   ```

3. **Check for HTTP Proxy URL**
   - In your RunPod dashboard, look for HTTP endpoints
   - You might see something like: `https://your-pod-id-8188.proxy.runpod.net`
   - Or check if port 8188 is listed in "Exposed Ports"

4. **Update Your App**
   If you find a proxy URL, update your `.env`:
   ```env
   RUNPOD_POD_URL=your-pod-id-8188.proxy.runpod.net
   RUNPOD_POD_PORT=443
   ```

## Option 2: Password Authentication

If RunPod provides a root password (check your dashboard):

1. **Find Root Password**
   - Look in your RunPod dashboard for "Root Password" or "Password"
   - It might be under "Connection Details"

2. **Connect with Password**
   ```bash
   ssh root@149.36.1.79 -p 33805 -L 8188:localhost:8188 -N
   ```
   Then enter the password when prompted.

## Option 3: Try Different SSH Key Format

The key might need to be in OpenSSH format:

1. **Convert Key (if needed)**
   ```bash
   ssh-keygen -p -m OpenSSH -f C:\Users\yvngt\.ssh\id_ed25519
   ```

2. **Try Connection Again**
   ```bash
   ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N
   ```

## Recommendation

**Try Option 1 first** - the web terminal is the most reliable way to access your pod and start ComfyUI. Once ComfyUI is running, check if RunPod provides an HTTP proxy URL for external access.

This avoids SSH issues entirely and gets your RTX 5090 connected to your Face Morphing app quickly.