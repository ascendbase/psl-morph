@echo off
echo 🗂️ Railway Volume Image Management Tool
echo ==========================================
echo.
echo This tool helps you manage and delete images from Railway volume storage.
echo.
echo Available operations:
echo - List all images in volume storage
echo - Find orphaned images (not referenced in database)
echo - Find old images (older than X days)
echo - Delete orphaned or old images
echo - Show storage statistics
echo.
pause
echo.
echo 🚀 Starting image management tool...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if the Python script exists
if not exist "delete_railway_volume_images.py" (
    echo ❌ Error: delete_railway_volume_images.py not found in current directory
    echo 📁 Current directory: %CD%
    echo.
    echo 💡 Make sure you're running this script from the project directory
    echo    where delete_railway_volume_images.py is located.
    echo.
    pause
    exit /b 1
)

echo 📁 Running from: %CD%
echo.
python delete_railway_volume_images.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Error occurred while running the image management tool.
    echo 💡 Possible solutions:
    echo    1. Make sure Python is installed and in your PATH
    echo    2. Make sure you're in the correct project directory
    echo    3. Check if all required Python modules are installed
    echo.
) else (
    echo.
    echo ✅ Image management completed successfully.
)

echo.
pause
