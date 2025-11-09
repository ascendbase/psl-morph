# Railway Manual Volume Creation Guide

## How to Create Facial Evaluation Volume via Railway Website

### Step 1: Access Your Railway Project
1. Go to [railway.app](https://railway.app)
2. Sign in to your account
3. Navigate to your project dashboard

### Step 2: Navigate to Volumes Section
1. In your project dashboard, look for the **"Volumes"** tab in the left sidebar
2. Click on **"Volumes"** to access the volume management section

### Step 3: Create New Volume
1. Click the **"Create Volume"** button (usually a blue/purple button)
2. Fill in the volume details:

#### Volume Configuration:
- **Name**: `facial-evaluations`
- **Mount Path**: `/app/facial_evaluations`
- **Size**: `1GB` (you can increase this later if needed)
- **Description** (optional): `Storage for facial evaluation images`

### Step 4: Confirm Creation
1. Review your settings:
   - ✅ Name: `facial-evaluations`
   - ✅ Mount Path: `/app/facial_evaluations`
   - ✅ Size: `1GB`
2. Click **"Create Volume"** to confirm

### Step 5: Verify Volume Creation
1. You should see the new volume listed in your volumes section
2. Status should show as "Active" or "Ready"
3. Note the mount path: `/app/facial_evaluations`

### Step 6: Deploy Your Application
1. Go back to your main project dashboard
2. Click **"Deploy"** or **"Redeploy"** to apply the volume changes
3. Wait for deployment to complete

## Volume Details

### What This Volume Does:
- **Purpose**: Stores facial evaluation images (original and morphed photos)
- **Persistence**: Images will survive app restarts and redeployments
- **Access**: Your app can read/write files to `/app/facial_evaluations/`

### File Structure in Volume:
```
/app/facial_evaluations/
├── user_123_original_20250810_123456.jpg
├── user_123_morphed_20250810_123456.jpg
├── user_456_original_20250810_234567.jpg
└── user_456_morphed_20250810_234567.jpg
```

## Troubleshooting

### If Volume Creation Fails:
1. **Check Quota**: Ensure you haven't exceeded your volume limit
2. **Verify Name**: Volume names must be unique within your project
3. **Check Mount Path**: Ensure `/app/facial_evaluations` is not already used

### If Volume Doesn't Appear:
1. Refresh the page
2. Check the "All Volumes" or "Project Volumes" filter
3. Verify you're in the correct project

### If App Can't Access Volume:
1. Ensure mount path is exactly `/app/facial_evaluations`
2. Redeploy your application after creating the volume
3. Check app logs for permission errors

## Alternative: Using Railway CLI

If the website method doesn't work, you can also use:

```bash
# Login to Railway
railway login

# Create volume
railway volume create facial-evaluations --mount-path /app/facial_evaluations --size 1GB

# List volumes to verify
railway volume list
```

## Next Steps After Volume Creation

1. ✅ Volume created: `facial-evaluations`
2. 🚀 Deploy your app with the new volume
3. 🧪 Test facial evaluation feature
4. 👨‍💼 Check admin dashboard: `/admin/facial-evaluations`
5. 📊 Monitor volume usage in Railway dashboard

## Important Notes

- **Billing**: Volumes are billed separately from compute time
- **Backup**: Consider backing up important evaluation data
- **Scaling**: You can increase volume size later if needed
- **Access**: Only your deployed app can access this volume

## Support

If you encounter issues:
1. Check Railway documentation: [docs.railway.app](https://docs.railway.app)
2. Railway Discord community
3. Railway support tickets

---

**Ready to proceed?** Once you've created the volume, your facial evaluation feature will have persistent storage for user images! 🎉
