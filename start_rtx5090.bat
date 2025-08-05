@echo off
echo Starting Face Morphing App with RTX 5090
echo ================================================

echo Loading environment variables from .env file...
set COMFYUI_URL=https://choa76vtevld8t-8188.proxy.runpod.net
set USE_CLOUD_GPU=true
set USE_RUNPOD_POD=true
set RUNPOD_POD_URL=choa76vtevld8t-8188.proxy.runpod.net
set RUNPOD_POD_PORT=443
set COMFYUI_TIMEOUT=300

echo RTX 5090 Configuration (FORCED CLOUD GPU):
echo   COMFYUI_URL: %COMFYUI_URL%
echo   USE_CLOUD_GPU: %USE_CLOUD_GPU%
echo   USE_RUNPOD_POD: %USE_RUNPOD_POD%
echo   RUNPOD_POD_URL: %RUNPOD_POD_URL%
echo.
echo WARNING: This app will ONLY use RTX 5090 cloud GPU!
echo Local GPU processing is DISABLED.

echo.
echo Starting Flask app with RTX 5090 configuration...
echo RTX 5090 is ready for face morphing!
echo ================================================

python app.py