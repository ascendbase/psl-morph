# Railway Volume Setup Guide - Step by Step

## 🚨 Current Issue
Your `railway.toml` has volumes configured, but they don't exist in Railway yet. You need to create them manually first.

## 📋 Step-by-Step Volume Creation

### **Step 1: Create the "uploads" Volume**

1. In your Railway dashboard, go to your project
2. Click on **"Volumes"** tab (or the volume icon)
3. Click **"Create Volume"** button
4. Fill in the details:
   - **Volume Name**: `uploads`
   - **Mount Path**: `/app/uploads`
   - **Size**: Start with `1GB` (you can increase later)
5. Click **"Create Volume"**

### **Step 2: Create the "outputs" Volume**

1. Click **"Create Volume"** again
2. Fill in the details:
   - **Volume Name**: `outputs`
   - **Mount Path**: `/app/outputs`
   - **Size**: Start with `2GB` (outputs are usually larger)
3. Click **"Create Volume"**

### **Step 3: Verify Volume Configuration**

After creating both volumes, you should see:
- ✅ `uploads` volume mounted at `/app/uploads`
- ✅ `outputs` volume mounted at `/app/outputs`

## 🔧 Alternative: CLI Method

If you prefer using the Railway CLI:

```bash
# Create uploads volume
railway volume create uploads --mount-path /app/uploads --size 1GB

# Create outputs volume  
railway volume create outputs --mount-path /app/outputs --size 2GB

# List volumes to verify
railway volume list
```

## 📁 What These Volumes Store

### **uploads Volume (`/app/uploads/`)**
- Original user images for facial evaluation
- Secondary images (if uploaded)
- Regular generation input images
- File naming: `eval_{uuid}.jpg`, `{uuid}.png`, etc.

### **outputs Volume (`/app/outputs/`)**
- Generated morph results
- Processed facial evaluation images
- File naming: `result_{id}_{timestamp}.png`

## 🚀 After Creating Volumes

### **Step 4: Redeploy Your App**

```bash
# Deploy with the new volumes
railway up
```

### **Step 5: Test Volume Access**

```bash
# Connect to Railway container
railway run bash

# Check if volumes are mounted
ls -la /app/
# Should show: uploads/ and outputs/ directories

# Test volume write access
touch /app/uploads/test.txt
touch /app/outputs/test.txt
ls -la /app/uploads/
ls -la /app/outputs/
```

## 🎯 Volume Size Recommendations

| Volume | Recommended Size | Purpose |
|--------|------------------|---------|
| `uploads` | **1-2GB** | User uploaded images |
| `outputs` | **2-5GB** | Generated results (larger files) |

You can always increase volume size later if needed.

## 🔍 Troubleshooting

### **Volumes Not Showing Up?**

1. **Check Railway Dashboard**: Go to your project → Volumes tab
2. **Verify Names Match**: Volume names must match `railway.toml` exactly
3. **Check Mount Paths**: Must be `/app/uploads` and `/app/outputs`

### **Permission Issues?**

Add this to your `Dockerfile` to ensure proper permissions:

```dockerfile
# Create directories and set permissions
RUN mkdir -p /app/uploads /app/outputs
RUN chmod 755 /app/uploads /app/outputs
```

### **Volumes Not Persistent?**

Make sure your `railway.toml` has the correct configuration:

```toml
[[deploy.volumes]]
name = "uploads"
mountPoint = "/app/uploads"

[[deploy.volumes]]
name = "outputs"
mountPoint = "/app/outputs"
```

## ✅ Verification Checklist

After setup, verify:

- [ ] `uploads` volume created in Railway dashboard
- [ ] `outputs` volume created in Railway dashboard  
- [ ] Both volumes show correct mount paths
- [ ] App deployed successfully with `railway up`
- [ ] Can access `/app/uploads/` and `/app/outputs/` in container
- [ ] Facial evaluation feature works end-to-end

## 🎉 Next Steps

Once volumes are set up:

1. **Test Facial Evaluation**: Upload an image and request evaluation
2. **Check Admin Dashboard**: View requests at `/admin/facial-evaluations`
3. **Verify Image Storage**: Images should persist across deployments
4. **Monitor Usage**: Check volume usage in Railway dashboard

Your facial evaluation feature will now have persistent image storage! 🚀

## 📞 Need Help?

If volumes still don't work:
1. Check Railway logs for mount errors
2. Verify your Railway plan supports volumes
3. Contact Railway support if needed

The volumes are essential for the facial evaluation feature to work properly in production.
