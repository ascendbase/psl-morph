# 🚀 How to Use Railway Volume Image Management Tool

## ✅ **FIXED: The batch script now works correctly!**

The issue was that the batch script wasn't running from the correct directory. I've fixed it to automatically change to the project directory.

## 📋 **Step-by-Step Usage Instructions**

### **Method 1: Using the Batch Script (Recommended)**

1. **Navigate to your project directory** in File Explorer:
   ```
   d:\Morph-app\
   ```

2. **Double-click on `clean_railway_images.bat`**
   - The script will automatically change to the correct directory
   - It will check if the Python script exists
   - It will show you the current directory before running

3. **Follow the interactive menu** that appears

### **Method 2: Using Command Prompt**

1. **Open Command Prompt**
2. **Navigate to your project directory**:
   ```cmd
   cd /d d:\Morph-app
   ```
3. **Run the Python script directly**:
   ```cmd
   python delete_railway_volume_images.py
   ```

### **Method 3: For Railway Production**

1. **Connect to Railway**:
   ```cmd
   railway shell
   ```
2. **Run the script**:
   ```cmd
   python delete_railway_volume_images.py
   ```

## 🔧 **Interactive Menu Options**

When you run the tool, you'll see:

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

### **Recommended First Steps:**

1. **Start with Option 6** - Show storage statistics
   - This gives you an overview of your storage usage
   - Shows total files and space used

2. **Try Option 2** - List orphaned images
   - These are safe to delete (not referenced in database)
   - Good for initial cleanup

3. **Use Option 4** - Delete orphaned images
   - Safest deletion option
   - Frees up space without affecting active data

## ⚠️ **Important Notes**

### **For Local Testing:**
- The tool will show "Volume path not found" - this is normal
- You won't have actual images to manage locally
- The tool will still demonstrate all functions

### **For Production Use:**
- Always start with orphaned images (safer)
- Be careful with old image deletion
- Consider backing up database before major cleanups

## 🛠️ **Troubleshooting**

### **If you get "Python not found":**
```cmd
# Check if Python is installed
python --version

# If not installed, install Python from python.org
```

### **If you get "Module not found":**
```cmd
# Install required modules
pip install flask sqlalchemy psycopg2-binary
```

### **If the script can't find the database:**
- Make sure your `.env` file has the correct `DATABASE_URL`
- For local testing, this is normal and expected

## 📊 **Example Usage Session**

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

❓ Choose an action (1-7): 6

📊 Storage Statistics:
📁 Volume path: /app/facial_evaluations
📊 Total images: 1,247
💾 Total size: 2.3 GB
📅 Newest image: 2024-01-15 14:30
📅 Oldest image: 2023-12-01 09:15

❓ Choose an action (1-7): 2

🧹 Orphaned Images (23 total):
  1. user_123_1640995200.jpg (2.1 MB) - 2024-01-01 12:00
  2. user_456_1640995300.jpg (1.8 MB) - 2024-01-01 12:05
  ... and 21 more images

❓ Choose an action (1-7): 4

📊 Found 23 images to delete
💾 Total size: 45.2 MB

❓ Are you sure you want to delete 23 images? (yes/no): yes

✅ Deleted: user_123_1640995200.jpg
✅ Deleted: user_456_1640995300.jpg
...

🎉 Successfully deleted 23 out of 23 images
```

## 🎯 **Quick Start**

1. **Double-click `clean_railway_images.bat`**
2. **Press any key to continue**
3. **Choose option 6** (Show storage statistics)
4. **Choose option 2** (List orphaned images)
5. **Choose option 4** (Delete orphaned images) if you want to clean up
6. **Choose option 7** (Exit) when done

That's it! The tool is now ready to use and will help you manage your Railway volume storage effectively.
