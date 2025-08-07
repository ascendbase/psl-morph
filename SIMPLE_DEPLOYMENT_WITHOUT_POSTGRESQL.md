# Simple Deployment Without PostgreSQL (Quick Test)

## If You Can't Add PostgreSQL Right Now

You can still deploy and test your app with the fixes applied. The database will reset on deployments, but you can test the ComfyUI integration.

## Quick Deployment Steps

### 1. Deploy Your Current App
```bash
# Run the deployment script
deploy_to_railway.bat
```

Or manually:
```bash
git add .
git commit -m "Fix: ComfyUI parameters + database config ready"
git push origin main
```

### 2. Test the ComfyUI Integration

1. **Make sure your local ComfyUI is running** on `http://127.0.0.1:8188`
2. **Upload an image** to your Railway app
3. **Click "Start Transformation"**
4. **Check if it calls your local ComfyUI** and generates images

### 3. What Will Work vs What Won't

✅ **Will Work**:
- ComfyUI parameter fix (no more errors)
- Image generation using your local GPU
- Custom features (eyes, nose, lips, etc.)
- Basic app functionality

❌ **Won't Persist**:
- User accounts (will reset on deployment)
- Generation history
- Payment records
- Any user data

## Environment Variable for Local ComfyUI

If Railway can't reach your local ComfyUI, you might need to:

### Option A: Use ngrok (Recommended for Testing)
```bash
# Install ngrok
# Download from https://ngrok.com/

# Expose your local ComfyUI
ngrok http 8188
```

Then set the Railway environment variable:
- `LOCAL_COMFYUI_URL` = `https://your-ngrok-url.ngrok.io`

### Option B: Use Cloudflare Tunnel
```bash
# Install cloudflared
# Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Create tunnel
cloudflared tunnel --url http://localhost:8188
```

## Testing Checklist

1. ✅ **App deploys without errors**
2. ✅ **No ComfyUI parameter mismatch errors**
3. ✅ **Can upload images**
4. ✅ **"Start Transformation" button works**
5. ✅ **Images are generated using local ComfyUI**
6. ✅ **Custom features work (eyes, nose, lips)**

## After Testing Successfully

Once you confirm the ComfyUI integration works:

1. **Add PostgreSQL to Railway** (using the updated guide)
2. **Redeploy** your app
3. **User data will now persist forever**

## Alternative: Railway CLI for PostgreSQL

If the web interface is confusing, try the CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Add PostgreSQL (correct syntax)
railway add --database postgres

# Deploy
railway up
```

---

**This approach lets you test the core functionality (ComfyUI integration) while working on the database persistence separately.**
