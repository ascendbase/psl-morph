# Image Storage Access Guide - Railway Volumes

## 📁 Where to Find Uploaded Images

### **Local Development Environment**

When running locally, images are stored in your project directory:

```
d:/Morph-app/
├── uploads/           ← Original & secondary images
│   ├── .gitkeep
│   ├── eval_abc123.jpg    ← Facial evaluation uploads
│   ├── def456.png         ← Regular generation uploads
│   └── eval_xyz789.jpg    ← More evaluation images
├── outputs/           ← Generated/morphed images
│   ├── .gitkeep
│   ├── result_123_456.png ← Generated morph results
│   └── result_789_012.png ← More results
```

**Access locally:**
```bash
# View uploads folder
dir uploads
ls uploads/

# View outputs folder  
dir outputs
ls outputs/

# Open folder in explorer
explorer uploads
explorer outputs
```

### **Railway Production Environment**

In Railway, images are stored in persistent volumes:

```
/app/                  ← Railway container
├── uploads/           ← Mounted volume (persistent)
│   ├── eval_abc123.jpg
│   ├── def456.png
│   └── eval_xyz789.jpg
├── outputs/           ← Mounted volume (persistent)
│   ├── result_123_456.png
│   └── result_789_012.png
```

## 🔍 How to Access Images in Railway

### **IMPORTANT: Railway Shell vs Railway Container**

⚠️ **Key Distinction:**
- `railway shell` = Sets environment variables locally (you're still on your local machine)
- `railway run bash` = Actually connects to the Railway container

### **Method 1: Access Railway Container (Recommended)**

```bash
# Connect to the actual Railway container (Linux environment)
railway run bash

# Once inside the Railway container (Linux commands):
ls -la /app/uploads/     # List uploaded images
ls -la /app/outputs/     # List generated images

# View image details with sizes
ls -lah /app/uploads/    # Human readable sizes
du -sh /app/uploads/*    # Size of each file

# Count files
find /app/uploads -type f | wc -l
find /app/outputs -type f | wc -l

# Check total folder size
du -sh /app/uploads
du -sh /app/outputs
```

### **Method 2: Railway Shell (Local with Environment Variables)**

```powershell
# This sets Railway environment variables but keeps you local
railway shell

# Check local uploads/outputs (your development environment):
Get-ChildItem uploads/      # Local uploads folder
Get-ChildItem outputs/      # Local outputs folder

# Note: /app/uploads/ doesn't exist locally - only in Railway container!
```

### **Method 2: Railway Dashboard**

1. Go to [railway.app](https://railway.app)
2. Select your project
3. Go to "Deployments" tab
4. Click on latest deployment
5. Click "View Logs"
6. In logs, you can see file operations

### **Method 3: Add Debug Endpoint (Temporary)**

Add this to your `app.py` for debugging (remove after testing):

```python
@app.route('/debug/list-images')
@login_required
def debug_list_images():
    """Debug endpoint to list all images (REMOVE IN PRODUCTION)"""
    if not current_user.is_admin:
        return "Access denied", 403
    
    import os
    
    uploads_files = []
    outputs_files = []
    
    # List uploads
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            if file != '.gitkeep':
                file_path = os.path.join(UPLOAD_FOLDER, file)
                size = os.path.getsize(file_path)
                uploads_files.append(f"{file} ({size} bytes)")
    
    # List outputs  
    if os.path.exists(OUTPUT_FOLDER):
        for file in os.listdir(OUTPUT_FOLDER):
            if file != '.gitkeep':
                file_path = os.path.join(OUTPUT_FOLDER, file)
                size = os.path.getsize(file_path)
                outputs_files.append(f"{file} ({size} bytes)")
    
    return f"""
    <h2>Debug: Image Files</h2>
    <h3>Uploads ({len(uploads_files)} files):</h3>
    <ul>{''.join(f'<li>{f}</li>' for f in uploads_files)}</ul>
    
    <h3>Outputs ({len(outputs_files)} files):</h3>
    <ul>{''.join(f'<li>{f}</li>' for f in outputs_files)}</ul>
    
    <p><strong>Upload Path:</strong> {UPLOAD_FOLDER}</p>
    <p><strong>Output Path:</strong> {OUTPUT_FOLDER}</p>
    """
```

Then visit: `https://your-app.railway.app/debug/list-images`

## 📊 Railway Volume Management

### **Check Volume Usage**

```bash
# Connect to Railway container (Linux environment)
railway run bash

# Check folder contents and sizes
du -sh /app/uploads/
du -sh /app/outputs/

# Count files
find /app/uploads -type f | wc -l
find /app/outputs -type f | wc -l

# List all files with details
ls -lah /app/uploads/
ls -lah /app/outputs/

# Check available disk space
df -h /app/uploads
df -h /app/outputs
```

**Alternative: Check from local with Railway shell**
```powershell
# This only works for local development files
railway shell
Get-ChildItem uploads/ | Measure-Object -Property Length -Sum
Get-ChildItem outputs/ | Measure-Object -Property Length -Sum
```

### **Volume Paths in Railway**

```
Railway Container Structure:
/app/                     ← Your application root
├── uploads/              ← Volume mount point
│   └── (persistent files)
├── outputs/              ← Volume mount point  
│   └── (persistent files)
├── app.py               ← Your application
├── models.py            ← Database models
└── templates/           ← HTML templates
```

## 🔧 Image File Naming Convention

### **Facial Evaluation Images**
```
uploads/eval_{uuid}.{ext}     ← Original images for evaluation
uploads/eval_{uuid}_2.{ext}   ← Secondary images (optional)
```

### **Generation Images**
```
uploads/{uuid}.{ext}          ← User uploaded images
outputs/result_{id}_{timestamp}.png  ← Generated results
```

### **Example Files**
```
uploads/
├── eval_a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg  ← Facial eval
├── eval_b2c3d4e5-f6g7-8901-bcde-f23456789012.png  ← Facial eval  
├── c3d4e5f6-g7h8-9012-cdef-345678901234.jpg       ← Regular upload

outputs/
├── result_123_1641234567.png  ← Generated morph
├── result_124_1641234890.png  ← Another morph
```

## 🛠️ Troubleshooting Image Access

### **Images Not Appearing?**

1. **First, make sure you're in the Railway container:**
```bash
# Connect to actual Railway container
railway run bash

# Check if you're in the container
pwd
# Should show: /app

# Check folder existence
ls -la /app/
# Should show uploads/ and outputs/ directories
```

2. **Check volume mounting:**
```bash
railway run bash
mount | grep app
# Should show volume mounts
```

3. **Check app configuration:**
```bash
railway run bash
echo $UPLOAD_FOLDER
echo $OUTPUT_FOLDER
# Should show absolute paths like /app/uploads
```

4. **If using railway shell (local environment):**
```powershell
railway shell
# Check local folders (development environment)
Test-Path uploads/
Test-Path outputs/
# These are your local development folders
```

### **Volume Not Persistent?**

Check `railway.toml`:
```toml
[[deploy.volumes]]
name = "uploads"
mountPoint = "/app/uploads"

[[deploy.volumes]]
name = "outputs" 
mountPoint = "/app/outputs"
```

## 📱 Admin Image Viewing

### **Through Web Interface**

As admin, you can view images through:

1. **Admin Dashboard**: `/admin/facial-evaluations`
2. **Image URLs**: `/facial-evaluation-image/<id>/<type>`
   - `type` can be: `original`, `morphed`, `secondary`

### **Direct Image Access**

```python
# In your admin interface, images are served via:
@app.route('/facial-evaluation-image/<evaluation_id>/<image_type>')
def get_facial_evaluation_image(evaluation_id, image_type):
    # This serves images from the volumes
    # Original: from /app/uploads/
    # Morphed: from /app/outputs/
    # Secondary: from /app/uploads/
```

## 💾 Backup Strategy

### **Download All Images**

```bash
# Connect to Railway container
railway run bash

# Compress all images (Linux)
tar -czf /tmp/images_backup.tar.gz /app/uploads /app/outputs

# Exit container
exit

# Download backup to local machine
railway run -- cat /tmp/images_backup.tar.gz > images_backup.tar.gz
```

**Alternative: Copy individual files**
```bash
# Copy specific file from Railway to local
railway run -- cat /app/uploads/filename.jpg > local_filename.jpg
```

### **Automated Backup**

Consider adding a backup endpoint:
```python
@app.route('/admin/backup-images')
@login_required
def backup_images():
    if not current_user.is_admin:
        return "Access denied", 403
    
    import tarfile
    import tempfile
    
    # Create backup archive
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        with tarfile.open(tmp.name, 'w:gz') as tar:
            tar.add(UPLOAD_FOLDER, arcname='uploads')
            tar.add(OUTPUT_FOLDER, arcname='outputs')
        
        return send_file(tmp.name, as_attachment=True, 
                        download_name=f'images_backup_{datetime.now().strftime("%Y%m%d")}.tar.gz')
```

## 🎯 Quick Access Summary

| Environment | Location | Access Method |
|-------------|----------|---------------|
| **Local** | `d:/Morph-app/uploads/` | File Explorer |
| **Local** | `d:/Morph-app/outputs/` | File Explorer |
| **Railway** | `/app/uploads/` | `railway shell` |
| **Railway** | `/app/outputs/` | `railway shell` |
| **Web** | Admin dashboard | Browser interface |
| **API** | `/facial-evaluation-image/` | HTTP endpoint |

Your images are safely stored in Railway volumes and will persist across deployments! 🎉
