@echo off
echo ========================================
echo   PRODUCTION LOCAL COMFYUI SETUP
echo ========================================
echo.
echo This will set up your local ComfyUI to serve your Railway app
echo Users worldwide will use your local GPU through Railway!
echo.

echo Step 1: Starting ComfyUI...
echo Make sure you have the required models:
echo - real-dream-15.safetensors (checkpoint)
echo - chad_sd1.5.safetensors (LoRA)
echo - FaceDetailer nodes installed
echo.

REM Check for common ComfyUI installations
if exist "D:\ComfyUI_windows_portable\run_nvidia_gpu.bat" (
    echo Found ComfyUI portable at D:\ComfyUI_windows_portable
    echo Starting with NVIDIA GPU support...
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && run_nvidia_gpu.bat"
) else if exist "D:\ComfyUI_windows_portable\ComfyUI\main.py" (
    echo Found ComfyUI at D:\ComfyUI_windows_portable\ComfyUI
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable\ComfyUI && python main.py"
) else if exist "D:\ComfyUI_windows_portable\main.py" (
    echo Found ComfyUI at D:\ComfyUI_windows_portable
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && python main.py"
) else if exist "C:\ComfyUI\main.py" (
    echo Found ComfyUI at C:\ComfyUI
    start "ComfyUI" cmd /k "cd /d C:\ComfyUI && python main.py"
) else if exist ".\ComfyUI\main.py" (
    echo Found ComfyUI in current directory
    start "ComfyUI" cmd /k "cd /d .\ComfyUI && python main.py"
) else (
    echo ComfyUI not found in common locations!
    echo Common locations checked:
    echo - D:\ComfyUI_windows_portable\run_nvidia_gpu.bat
    echo - D:\ComfyUI_windows_portable\ComfyUI\main.py
    echo - D:\ComfyUI_windows_portable\main.py
    echo - C:\ComfyUI\main.py
    echo - .\ComfyUI\main.py
    echo.
    echo Please enter the full path to your ComfyUI folder:
    set /p comfyui_path="ComfyUI path: "
    if exist "%comfyui_path%\run_nvidia_gpu.bat" (
        echo Starting ComfyUI with NVIDIA GPU support...
        start "ComfyUI" cmd /k "cd /d %comfyui_path% && run_nvidia_gpu.bat"
    ) else if exist "%comfyui_path%\main.py" (
        start "ComfyUI" cmd /k "cd /d %comfyui_path% && python main.py"
    ) else (
        echo Error: Neither run_nvidia_gpu.bat nor main.py found in %comfyui_path%
        echo Please check the path and try again.
        pause
        exit /b 1
    )
)

echo.
echo Waiting 15 seconds for ComfyUI to start...
timeout /t 15

echo.
echo Step 2: Starting ngrok tunnel...
echo This will expose your ComfyUI to the internet securely
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting ngrok tunnel on port 8188...
    start "ngrok" cmd /k "ngrok http 8188"
) else (
    echo ngrok not found! Please install ngrok first:
    echo 1. Download from: https://ngrok.com/download
    echo 2. Extract to a folder in your PATH
    echo 3. Sign up and get your authtoken
    echo 4. Run: ngrok config add-authtoken YOUR_AUTHTOKEN
    echo.
    pause
    exit /b 1
)

echo.
echo Waiting 10 seconds for ngrok to start...
timeout /t 10

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Your local ComfyUI is now accessible to Railway!
echo.
echo Next steps:
echo 1. Check the ngrok window for your public URL (e.g., https://abc123.ngrok.io)
echo 2. Go to your Railway project dashboard
echo 3. Add these environment variables:
echo    - USE_LOCAL_COMFYUI=true
echo    - USE_MODAL=false
echo    - USE_CLOUD_GPU=false
echo    - LOCAL_COMFYUI_URL=https://your-ngrok-url.ngrok.io
echo    - LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json
echo 4. Deploy your Railway app
echo 5. Test with users worldwide!
echo.
echo Your Railway app will now use your local GPU for processing!
echo Users can upload images globally and get results from your hardware.
echo.
echo IMPORTANT: Keep this window open and your computer running
echo to serve users. Close ngrok tunnel to stop serving.
echo.

pause
