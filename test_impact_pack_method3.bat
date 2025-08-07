@echo off
echo ========================================
echo Testing Method 3: Pre-install Dependencies
echo ========================================
echo.
echo Installing dependencies first...
pip install opencv-python-headless ultralytics segment-anything
pip install scipy scikit-image insightface onnxruntime
pip install mediapipe albumentations kornia timm addict yapf
echo.
echo Dependencies installed. Now:
echo 1. Navigate to your ComfyUI/custom_nodes folder
echo 2. Run: git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
echo 3. DO NOT run pip install -r requirements.txt
echo 4. Restart ComfyUI
echo 5. Check console for "ComfyUI-Impact-Pack: loaded successfully"
echo.
pause
