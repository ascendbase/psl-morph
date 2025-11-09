# 🗂️ Railway Volume Image Management Guide

This guide explains how to manage and delete images stored in Railway volume storage for the facial evaluation feature.

## 📋 Overview

The facial evaluation feature stores user-uploaded images in Railway volume storage at `/app/facial_evaluations/`. Over time, this can accumulate many images and consume storage space. This guide provides tools and methods to manage these images effectively.

## 🛠️ Available Tools

### 1. **Interactive Management Tool**
- **File**: `delete_railway_volume_images.py`
- **Launcher**: `clean_railway_images.bat`
- **Purpose**: Interactive command-line tool for comprehensive image management

### 2. **Features Available**
- ✅ List all images in volume storage
- ✅ Find orphaned images (not referenced in database)
- ✅ Find old images (older than X days)
- ✅ Delete orphaned or old images with confirmation
- ✅ Show detailed storage statistics
- ✅ Safe deletion with database cross-reference

## 🚀 How to Use

### **Method 1: Using the Batch Script (Easiest)**
```bash
# Double-click or run from command line
clean_railway_images.bat
```

### **Method 2: Direct Python Execution**
```bash
# Run the Python script directly
python delete_railway_volume_images.py
```

### **Method 3: Railway CLI (Production)**
```bash
# Connect to Railway deployment
railway shell
python delete_railway_volume_images.py
```

## 📊 Interactive Menu Options

When you run the tool, you'll see this menu:

```
🔧 Available Actions:
1. 📋 List all images
2. 🧹 List orphaned images (not in database)
3. ⏰ List old images (older than X days)
4. 🗑️ Delete orphaned images
5. 🗑️ Delete old images
6. 📊 Show storage statistics
7. 🚪 Exit
```

### **Option 1: List All Images**
- Shows all images in the volume storage
- Displays file name, size, and modification date
- Useful for getting an overview of stored images

### **Option 2: List Orphaned Images**
- Finds images that exist in storage but are not referenced in the database
- These are safe to delete as they're not linked to any facial evaluations
- Usually occurs when database records are deleted but files remain

### **Option 3: List Old Images**
- Finds images older than a specified number of days (default: 30)
- Useful for cleaning up old facial evaluation data
- You can specify any number of days

### **Option 4: Delete Orphaned Images**
- Safely deletes images not referenced in the database
- Shows confirmation prompt with details before deletion
- Provides summary of deleted files and space freed

### **Option 5: Delete Old Images**
- Deletes images older than specified days
- ⚠️ **Warning**: This will delete images that may still be referenced in the database
- Use with caution - consider backing up important data first

### **Option 6: Storage Statistics**
- Shows total number of images
- Displays total storage space used
- Shows newest and oldest image dates
- Provides volume path information

## 🔒 Safety Features

### **Database Cross-Reference**
- The tool checks the database before marking images as orphaned
- Prevents accidental deletion of images still in use
- Cross-references both `facial_evaluations` and `generations` tables

### **Confirmation Prompts**
- All deletion operations require explicit confirmation
- Shows detailed list of files to be deleted
- Displays total size that will be freed

### **Error Handling**
- Graceful handling of missing files
- Clear error messages for failed operations
- Continues processing even if individual files fail

## 📁 Storage Structure

```
/app/facial_evaluations/
├── user_123_1234567890.jpg     # Primary facial evaluation image
├── user_123_1234567890_2.jpg   # Secondary facial evaluation image
├── user_456_1234567891.jpg     # Another user's image
└── ...
```

### **File Naming Convention**
- Format: `user_{user_id}_{timestamp}.{extension}`
- Secondary images: `user_{user_id}_{timestamp}_2.{extension}`
- Supported formats: PNG, JPG, JPEG, WebP

## 🗑️ Deletion Strategies

### **Strategy 1: Regular Cleanup (Recommended)**
```bash
# Run monthly to clean orphaned images
python delete_railway_volume_images.py
# Choose option 4 (Delete orphaned images)
```

### **Strategy 2: Age-Based Cleanup**
```bash
# Delete images older than 90 days
python delete_railway_volume_images.py
# Choose option 5, enter 90 days
```

### **Strategy 3: Storage Emergency**
```bash
# When storage is critically low
python delete_railway_volume_images.py
# First try option 4 (orphaned)
# Then option 5 with shorter timeframe (30 days)
```

## 📊 Example Usage Session

```
🗂️ Railway Volume Image Management Tool
==================================================
📁 Volume path: /app/facial_evaluations
📊 Total images: 1,247
💾 Total size: 2.3 GB

🔧 Available Actions:
1. 📋 List all images
2. 🧹 List orphaned images (not in database)
3. ⏰ List old images (older than X days)
4. 🗑️ Delete orphaned images
5. 🗑️ Delete old images
6. 📊 Show storage statistics
7. 🚪 Exit

❓ Choose an action (1-7): 4

🧹 Orphaned Images (23 total):
  1. user_123_1640995200.jpg (2.1 MB) - 2024-01-01 12:00
  2. user_456_1640995300.jpg (1.8 MB) - 2024-01-01 12:05
  ... and 21 more images

📊 Found 23 images to delete
💾 Total size: 45.2 MB

❓ Are you sure you want to delete 23 images? (yes/no): yes

✅ Deleted: user_123_1640995200.jpg
✅ Deleted: user_456_1640995300.jpg
...

🎉 Successfully deleted 23 out of 23 images
```

## ⚠️ Important Warnings

### **Before Deleting Old Images**
- **Backup Important Data**: Consider backing up the database before bulk deletions
- **Check Business Requirements**: Ensure you're not violating data retention policies
- **Test First**: Try with a small number of days first to see what would be deleted

### **Production Considerations**
- **Maintenance Window**: Run during low-traffic periods
- **Monitor Storage**: Keep track of storage usage trends
- **Regular Schedule**: Set up regular cleanup schedules

## 🔧 Advanced Usage

### **Programmatic Usage**
You can import and use the functions in your own scripts:

```python
from delete_railway_volume_images import list_orphaned_images, delete_images

# Get orphaned images
orphaned = list_orphaned_images()
print(f"Found {len(orphaned)} orphaned images")

# Delete without confirmation (use carefully!)
delete_images(orphaned, confirm=False)
```

### **Custom Filtering**
Modify the script to add custom filtering logic:
- Filter by file size
- Filter by specific users
- Filter by date ranges
- Filter by file types

## 📈 Monitoring Storage Usage

### **Regular Checks**
```bash
# Quick storage overview
python delete_railway_volume_images.py
# Choose option 6 for statistics
```

### **Automated Monitoring**
Consider setting up automated alerts when storage usage exceeds thresholds:
- 80% capacity: Warning
- 90% capacity: Critical
- 95% capacity: Emergency cleanup needed

## 🆘 Emergency Cleanup

If storage is critically low:

1. **Immediate Action**:
   ```bash
   python delete_railway_volume_images.py
   # Option 4: Delete all orphaned images
   ```

2. **If Still Low**:
   ```bash
   # Delete images older than 30 days
   # Option 5, enter 30
   ```

3. **Last Resort**:
   ```bash
   # Delete images older than 7 days
   # Option 5, enter 7
   # ⚠️ This may delete recent facial evaluations!
   ```

## 📞 Support

If you encounter issues:
1. Check the error messages for specific problems
2. Ensure you have proper file permissions
3. Verify the volume path exists
4. Check database connectivity
5. Review the logs for detailed error information

## 🔄 Regular Maintenance Schedule

**Recommended Schedule**:
- **Weekly**: Check storage statistics
- **Monthly**: Delete orphaned images
- **Quarterly**: Review and delete old images (90+ days)
- **Annually**: Full storage audit and cleanup

This approach ensures optimal storage usage while maintaining data integrity and user experience.
