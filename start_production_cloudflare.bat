@echo off
REM =======================================
REM   PRODUCTION CLOUDFLARE TUNNEL SETUP (with automatic notifier)
REM =======================================
echo.
echo ========================================
echo   PRODUCTION CLOUDFLARE TUNNEL SETUP (with automatic notifier)
echo ========================================
echo.

REM Repository directory (where this .bat lives)
set "REPO_DIR=%~dp0"
set "LOG=%REPO_DIR%cloudflared.log"
set "WEBHOOK=https://psl-morph-production.up.railway.app/register-tunnel"
set "SECRET=morphpas"

REM Basic checks for required tools
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo cloudflared not found in PATH.
    echo Please install cloudflared and add it to PATH:
    echo https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo Python not found in PATH.
        echo Please install Python and ensure 'python' or 'py' is on PATH.
        pause
        exit /b 1
    ) else (
        set "PY_CMD=py"
    )
) else (
    set "PY_CMD=python"
)

echo Using python command: %PY_CMD%
echo Log file will be: %LOG%
echo Webhook: %WEBHOOK%
echo.

REM Step 1: Start ComfyUI (try common locations). Each starts in its own window.
echo Step 1: Starting ComfyUI...
if exist "D:\ComfyUI_windows_portable\run_nvidia_gpu.bat" (
    echo Found ComfyUI portable at D:\ComfyUI_windows_portable
    echo Starting with NVIDIA GPU support...
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && run_nvidia_gpu.bat"
) else if exist "D:\ComfyUI_windows_portable\ComfyUI\main.py" (
    echo Found ComfyUI at D:\ComfyUI_windows_portable\ComfyUI
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable\ComfyUI && %PY_CMD% main.py --listen --port 8188"
) else if exist "D:\ComfyUI_windows_portable\main.py" (
    echo Found ComfyUI at D:\ComfyUI_windows_portable
    start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable && %PY_CMD% main.py --listen --port 8188"
) else if exist "C:\ComfyUI\main.py" (
    echo Found ComfyUI at C:\ComfyUI
    start "ComfyUI" cmd /k "cd /d C:\ComfyUI && %PY_CMD% main.py --listen --port 8188"
) else if exist "%REPO_DIR%ComfyUI\main.py" (
    echo Found ComfyUI in repo folder
    start "ComfyUI" cmd /k "cd /d "%REPO_DIR%ComfyUI" && %PY_CMD% main.py --listen --port 8188"
) else (
    echo ComfyUI not found in common locations.
    echo Please enter the full path to your ComfyUI folder and press Enter:
    set /p comfyui_path="ComfyUI path: "
    if "%comfyui_path%"=="" (
        echo No path entered. Skipping automatic ComfyUI start. Ensure ComfyUI is running on port 8188.
    ) else (
        if exist "%comfyui_path%\run_nvidia_gpu.bat" (
            echo Starting ComfyUI with NVIDIA GPU support...
            start "ComfyUI" cmd /k "cd /d "%comfyui_path%" && run_nvidia_gpu.bat"
        ) else if exist "%comfyui_path%\main.py" (
            start "ComfyUI" cmd /k "cd /d "%comfyui_path%" && %PY_CMD% main.py --listen --port 8188"
        ) else (
            echo Error: Neither run_nvidia_gpu.bat nor main.py found in %comfyui_path%
            echo Please check the path and start ComfyUI manually.
        )
    )
)

echo Waiting 12 seconds for ComfyUI to start...
timeout /t 12 /nobreak >nul

REM Step 2: Start Cloudflared tunnel with automatic URL capture and registration
echo.
echo Step 2: Starting Cloudflare Tunnel with automatic registration...

REM Create a temporary batch file for tunnel monitoring
echo @echo off > "%REPO_DIR%temp_tunnel_monitor.bat"
echo set "WEBHOOK=%WEBHOOK%" >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo set "SECRET=%SECRET%" >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo set "PY_CMD=%PY_CMD%" >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo set "REPO_DIR=%REPO_DIR%" >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo. >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo echo Starting cloudflared tunnel... >> "%REPO_DIR%temp_tunnel_monitor.bat"
echo cloudflared tunnel --url http://localhost:8188 ^| "%REPO_DIR%temp_tunnel_parser.bat" >> "%REPO_DIR%temp_tunnel_monitor.bat"

REM Create tunnel URL parser
echo @echo off > "%REPO_DIR%temp_tunnel_parser.bat"
echo setlocal enabledelayedexpansion >> "%REPO_DIR%temp_tunnel_parser.bat"
echo :loop >> "%REPO_DIR%temp_tunnel_parser.bat"
echo set /p line= >> "%REPO_DIR%temp_tunnel_parser.bat"
echo if "!line!"=="" goto loop >> "%REPO_DIR%temp_tunnel_parser.bat"
echo echo !line! >> "%REPO_DIR%temp_tunnel_parser.bat"
echo echo !line! ^| findstr "trycloudflare.com" >nul >> "%REPO_DIR%temp_tunnel_parser.bat"
echo if !errorlevel! equ 0 ( >> "%REPO_DIR%temp_tunnel_parser.bat"
echo   for /f "tokens=*" %%%%a in ('echo !line! ^| findstr /r "https://[a-zA-Z0-9-]*\.trycloudflare\.com"') do ( >> "%REPO_DIR%temp_tunnel_parser.bat"
echo     for /f "tokens=*" %%%%b in ('echo %%%%a ^| findstr /r /c:"https://[a-zA-Z0-9-]*\.trycloudflare\.com"') do ( >> "%REPO_DIR%temp_tunnel_parser.bat"
echo       set "TUNNEL_URL=%%%%b" >> "%REPO_DIR%temp_tunnel_parser.bat"
echo       echo Found tunnel URL: !TUNNEL_URL! >> "%REPO_DIR%temp_tunnel_parser.bat"
echo       echo Registering with Railway... >> "%REPO_DIR%temp_tunnel_parser.bat"
echo       curl -H "Content-Type: application/json" -H "X-TUNNEL-SECRET: %SECRET%" -d "{\"url\":\"!TUNNEL_URL!\"}" "%WEBHOOK%" >> "%REPO_DIR%temp_tunnel_parser.bat"
echo       echo Registration complete! >> "%REPO_DIR%temp_tunnel_parser.bat"
echo     ) >> "%REPO_DIR%temp_tunnel_parser.bat"
echo   ) >> "%REPO_DIR%temp_tunnel_parser.bat"
echo ) >> "%REPO_DIR%temp_tunnel_parser.bat"
echo goto loop >> "%REPO_DIR%temp_tunnel_parser.bat"

start "Cloudflare Tunnel (Auto-Register)" cmd /k ""%REPO_DIR%temp_tunnel_monitor.bat""

echo Waiting 8 seconds for cloudflared to initialize and register...
timeout /t 8 /nobreak >nul

echo.
echo Setup launched. Three windows were started:
echo  - ComfyUI (if found)
echo  - Cloudflared tunnel (visible output)
echo  - Notifier (will POST to %WEBHOOK% once)
echo.
echo If notifier did not register the URL automatically, you can test the webhook with:
echo curl -H "Content-Type: application/json" -H "X-TUNNEL-SECRET: %SECRET%" -d "{\"url\":\"https://your-tunnel.trycloudflare.com\"}" %WEBHOOK%
echo.
echo Keep the cloudflared window open to continue serving.
echo Press any key to close this launcher window.
pause
