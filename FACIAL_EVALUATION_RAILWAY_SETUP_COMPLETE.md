# Facial Evaluation Railway Setup - Complete Guide

## 🎯 Current Status

✅ **Facial evaluation feature implemented** - All code is ready
✅ **Database schema updated** - PostgreSQL tables created
✅ **Railway configuration ready** - `railway.toml` has volume config
❌ **Railway volumes missing** - Need to create them manually

## 🚨 The Problem

Your `railway.toml` file has volume configuration:
```toml
[[deploy.volumes]]
name = "uploads"
mountPoint = "/app/uploads"

[[deploy.volumes]]
name = "outputs"
mountPoint = "/app/outputs"
```

But the actual volumes don't exist in Railway yet! This is why images aren't persisting.

## 🛠️ Solution: Create Railway Volumes

### **Option 1: Use the Automated Script (Recommended)**

```bash
# Run the volume creation script
./create_railway_volumes.bat
```

### **Option 2: Manual Creation via Railway Dashboard**

1. Go to your Railway project dashboard
2. Click **"Volumes"** tab
3. Click **"Create Volume"**
4. Create first volume:
   - **Name**: `uploads`
   - **Mount Path**: `/app/uploads`
   - **Size**: `1GB`
5. Create second volume:
   - **Name**: `outputs`
   - **Mount Path**: `/app/outputs`
   - **Size**: `2GB`

### **Option 3: Railway CLI Commands**

```bash
# Create uploads volume
railway volume create uploads --mount-path /app/uploads --size 1GB

# Create outputs volume
railway volume create outputs --mount-path /app/outputs --size 2GB

# Verify volumes
railway volume list
```

## 🚀 After Creating Volumes

### **Step 1: Deploy Your App**
```bash
railway up
```

### **Step 2: Test the Feature**

1. **Visit your app**: `https://your-app.railway.app`
2. **Register/Login** as a regular user
3. **Generate a morph** (any feature)
4. **After generation**: Look for "Request personal rating and facial features analysis"
5. **Click the button** - Should cost 20 credits
6. **Upload face image** for evaluation
7. **Submit request**

### **Step 3: Admin Response**

1. **Login as admin** (your account)
2. **Go to**: `/admin/facial-evaluations`
3. **View pending requests** with images
4. **Send response** back to user

### **Step 4: User Receives Response**

1. **User goes to**: Dashboard → "Facial Evaluation Requests"
2. **Status changes** from "Pending" to shows your response
3. **Images persist** across deployments

## 📁 What Gets Stored

### **uploads Volume (`/app/uploads/`)**
```
eval_abc123.jpg     ← User's original face image
eval_abc123_2.jpg   ← Secondary image (optional)
def456.png          ← Regular generation uploads
```

### **outputs Volume (`/app/outputs/`)**
```
result_123_456.png  ← Generated morph results
result_789_012.png  ← More morph results
```

## 🔍 Verify Everything Works

### **Check Volumes Are Mounted**
```bash
# Connect to Railway container
railway run bash

# Check volumes exist
ls -la /app/
# Should show: uploads/ and outputs/ directories

# Test write access
touch /app/uploads/test.txt
touch /app/outputs/test.txt
```

### **Check Facial Evaluation Flow**

1. ✅ User can request facial evaluation (costs 20 credits)
2. ✅ Images upload to `/app/uploads/eval_*.jpg`
3. ✅ Admin sees request with images at `/admin/facial-evaluations`
4. ✅ Admin can send response
5. ✅ User receives response in dashboard
6. ✅ Images persist across deployments

## 🎉 Feature Overview

### **For Users:**
- **After morph generation**: See "Request personal rating" message
- **Click button**: Upload face image (costs 20 credits)
- **Dashboard page**: "Facial Evaluation Requests" shows status
- **Receive response**: From admin with detailed analysis

### **For Admin (You):**
- **Admin dashboard**: `/admin/facial-evaluations`
- **View requests**: See original + morphed images
- **Send responses**: Detailed facial analysis
- **Track all requests**: Complete history

### **Credit System:**
- **Cost**: 20 credits per facial evaluation request
- **Low balance**: Prompts user to buy more credits first
- **Integrated**: With existing payment system

## 🔧 Troubleshooting

### **Volumes Not Working?**
1. Check Railway dashboard shows both volumes
2. Verify mount paths: `/app/uploads` and `/app/outputs`
3. Redeploy: `railway up`

### **Images Not Persisting?**
1. Volumes must be created before deployment
2. Check Railway logs for mount errors
3. Verify volume names match `railway.toml` exactly

### **Feature Not Showing?**
1. Database migration needed: Run facial evaluation setup scripts
2. Check user has enough credits (20 required)
3. Verify admin account is set up correctly

## 📋 Complete Checklist

- [ ] Create `uploads` volume in Railway (1GB)
- [ ] Create `outputs` volume in Railway (2GB)
- [ ] Deploy app: `railway up`
- [ ] Test user flow: Generate morph → Request evaluation
- [ ] Test admin flow: View requests → Send response
- [ ] Verify images persist across deployments
- [ ] Check credit deduction works (20 credits)

## 🎯 Next Steps

Once volumes are set up:

1. **Marketing**: Promote the new facial evaluation service
2. **Pricing**: Consider if 20 credits is the right price
3. **Analytics**: Track usage and user satisfaction
4. **Expansion**: Add more detailed analysis features

Your facial evaluation feature is now ready for production! 🚀

## 📞 Support

If you need help:
1. Check `RAILWAY_VOLUME_SETUP_GUIDE.md` for detailed instructions
2. Check `IMAGE_STORAGE_ACCESS_GUIDE.md` for accessing stored images
3. Run `create_railway_volumes.bat` for automated setup

The feature is fully implemented - you just need to create the Railway volumes!
