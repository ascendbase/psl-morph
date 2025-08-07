@echo off
echo ========================================
echo   FACE MORPH APP - LOCAL COMFYUI MODE
echo ========================================
echo.
echo This will start the Face Morph app using your local ComfyUI
echo Make sure ComfyUI is running on http://127.0.0.1:8188
echo.

REM Set environment variables for local ComfyUI
set USE_LOCAL_COMFYUI=true
set USE_MODAL=false
set USE_CLOUD_GPU=false
set COMFYUI_URL=http://127.0.0.1:8188
set LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json

echo Configuration:
echo - Local ComfyUI: ENABLED
echo - Modal.com: DISABLED
echo - Cloud GPU: DISABLED
echo - ComfyUI URL: %COMFYUI_URL%
echo - Workflow: %LOCAL_COMFYUI_WORKFLOW%
echo.

REM Test ComfyUI connection first
echo Testing ComfyUI connection...
python test_local_comfyui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: ComfyUI test failed!
    echo Please make sure:
    echo 1. ComfyUI is running on http://127.0.0.1:8188
    echo 2. All required nodes are installed (FaceDetailer, Impact Pack, etc.)
    echo 3. The workflow file exists: %LOCAL_COMFYUI_WORKFLOW%
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Face Morph App with Local ComfyUI...
echo.
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python app.py

pause
