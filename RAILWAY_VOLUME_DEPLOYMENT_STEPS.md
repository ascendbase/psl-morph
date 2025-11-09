# Railway Volume Setup for Facial Evaluation Feature

## ✅ Current Status
The Railway volume configuration is **already set up** in your `railway.toml` file:

```toml
[[deploy.volumes]]
name = "facial-evaluations"
mountPath = "/app/facial_evaluations"
```

## What You Need to Do

### Option 1: Automatic Volume Creation (Recommended)
**Nothing!** Railway will automatically create the volume when you deploy. The volume configuration in `railway.toml` tells Railway to:

1. Create a persistent volume named "facial-evaluations"
2. Mount it at `/app/facial_evaluations` in your container
3. Keep all files stored there permanently (survives deployments)

### Option 2: Manual Volume Creation (If needed)
If for some reason the automatic creation doesn't work, you can manually create the volume:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Volumes" tab
4. Click "New Volume"
5. Set:
   - **Name**: `facial-evaluations`
   - **Mount Path**: `/app/facial_evaluations`
   - **Size**: 1GB (should be plenty for images)

## How It Works

### During Deployment:
1. Railway reads `railway.toml`
2. Creates/attaches the "facial-evaluations" volume
3. Mounts it at `/app/facial_evaluations`
4. Your app can now store facial evaluation images permanently

### File Storage:
- **Temporary files**: `/app/uploads`, `/app/outputs` (deleted on redeploy)
- **Permanent files**: `/app/facial_evaluations` (persisted via volume)

## Verification

After deployment, you can verify the volume is working by:

1. Check Railway dashboard → Your Service → Volumes tab
2. Should see "facial-evaluations" volume listed
3. When users submit facial evaluations, images will be stored permanently

## No Additional Configuration Needed

✅ **Volume configuration**: Already in `railway.toml`  
✅ **App code**: Already configured to use `/app/facial_evaluations`  
✅ **Database**: Already has facial evaluation tables  
✅ **Templates**: Already created for user and admin interfaces  

**You're ready to deploy!** The facial evaluation feature will work immediately after deployment.

## Cost Considerations

- Railway volumes are typically $0.25/GB/month
- 1GB should handle thousands of facial evaluation images
- Only images specifically submitted for evaluation are stored (not all generation images)

## Troubleshooting

If images aren't persisting after deployment:
1. Check Railway dashboard → Volumes tab
2. Verify volume is mounted at `/app/facial_evaluations`
3. Check app logs for any permission errors
4. Ensure volume size isn't full (upgrade if needed)
