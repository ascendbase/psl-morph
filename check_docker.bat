@echo off
echo Checking Docker status...
echo.

REM Try to get Docker info with a timeout
docker info >nul 2>&1

if errorlevel 1 (
    echo ❌ Docker is NOT running or not responding!
    echo.
    echo Solutions:
    echo 1. Start Docker Desktop
    echo 2. Wait for it to fully load (whale icon should be solid, not animated)
    echo 3. If Docker is running but frozen, restart it:
    echo    - Right-click Docker Desktop icon
    echo    - Click "Quit Docker Desktop"
    echo    - Wait 10 seconds
    echo    - Start Docker Desktop again
    echo.
) else (
    echo ✅ Docker is running and responding!
    echo.
    echo You can now run build_and_push_comfyui.bat
    echo.
)

pause
