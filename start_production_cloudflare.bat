@echo off
echo ========================================
echo   PRODUCTION CLOUDFLARE TUNNEL SETUP
echo ========================================
echo.

echo Step 1: Starting ComfyUI...
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

echo Waiting 15 seconds for ComfyUI to start...
timeout /t 15

echo.
echo Step 2: Starting Cloudflare Tunnel...
echo This will expose your ComfyUI to the internet securely
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting Cloudflare tunnel on port 8188...
    start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8188"
) else (
    echo cloudflared not found! Please install it first:
    echo 1. Download from: https://github.com/cloudflare/cloudflared/releases/latest
    echo 2. Download cloudflared-windows-amd64.exe
    echo 3. Rename to cloudflared.exe
    echo 4. Move to C:\cloudflared\
    echo 5. Add C:\cloudflared to your PATH
    echo.
    pause
    exit /b 1
)

echo.
echo Waiting 10 seconds for tunnel to start...
timeout /t 10

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Your local ComfyUI is now accessible to Railway!
echo.
echo Next steps:
echo 1. Check the Cloudflare Tunnel window for your public URL
echo 2. Copy the URL (e.g., https://abc-def-ghi.trycloudflare.com)
echo 3. Go to your Railway project dashboard
echo 4. Add these environment variables:
echo    - USE_LOCAL_COMFYUI=true
echo    - USE_MODAL=false
echo    - USE_CLOUD_GPU=false
echo    - LOCAL_COMFYUI_URL=https://your-cloudflare-url.trycloudflare.com
echo    - LOCAL_COMFYUI_WORKFLOW=comfyui_workflows/workflow_facedetailer.json
echo 5. Deploy your Railway app
echo 6. Test with users worldwide!
echo.
echo Your Railway app will now use your local GPU for processing!
echo Users can upload images globally and get results from your hardware.
echo.
echo IMPORTANT: Keep both windows open to serve users
echo Close the tunnel window to stop serving.
echo.

pause
