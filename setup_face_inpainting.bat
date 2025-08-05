@echo off
echo 🎭 Face Inpainting Setup Script
echo ===============================

echo.
echo This script will help you set up the Face Inpainting workflow
echo which replaces ReActor with better face masking and compositing.
echo.

echo 📋 What this workflow does:
echo 1. Detects face area using SAM (Segment Anything Model)
echo 2. Creates precise mask around the face
echo 3. Inpaints only the face area with your LoRA
echo 4. Seamlessly blends with original image
echo.

set /p "comfyui_path=Enter your ComfyUI directory path (e.g., D:\ComfyUI_windows_portable\ComfyUI): "

if not exist "%comfyui_path%" (
    echo ❌ ComfyUI directory not found: %comfyui_path%
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo ✅ ComfyUI directory found: %comfyui_path%

echo.
echo 📦 Installing SAM extension for face detection...
cd /d "%comfyui_path%\custom_nodes"

if exist "comfyui_segment_anything" (
    echo ⚠️  SAM extension already exists, updating...
    cd comfyui_segment_anything
    git pull
) else (
    echo 📥 Downloading SAM extension...
    git clone https://github.com/storyicon/comfyui_segment_anything.git
    cd comfyui_segment_anything
)

echo 📦 Installing SAM dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install SAM dependencies
    echo Try running: pip install segment-anything opencv-python
    pause
    exit /b 1
)

echo ✅ SAM extension installed successfully

echo.
echo 📥 The SAM model will be downloaded automatically on first use (~2GB)
echo This may take a few minutes the first time you run the workflow.

echo.
echo 🔧 Next steps:
echo 1. Restart ComfyUI to load the new extension
echo 2. Start ComfyUI with: python main.py --listen 127.0.0.1 --port 8188
echo 3. Test the workflow manually in ComfyUI first
echo 4. Run the Face Morphing Web App: python app.py
echo.

echo ✅ Face Inpainting setup complete!
echo The app is now configured to use face masking instead of ReActor.
echo.

pause