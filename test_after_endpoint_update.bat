@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   TESTING UPDATED RUNPOD ENDPOINT
echo ========================================
echo.
echo Current directory: %CD%
echo.
echo This will test your endpoint after updating
echo the Docker image to: ascendbase/face-morphing-comfyui:latest
echo.
echo Make sure you have:
echo   1. Updated the endpoint Docker image
echo   2. Waited for endpoint to restart (2-3 minutes)
echo   3. Endpoint shows "Ready" status
echo.
pause
echo.
echo Testing endpoint...
if exist "test_new_endpoint_with_wait.py" (
    python test_new_endpoint_with_wait.py
) else (
    echo ERROR: test_new_endpoint_with_wait.py not found in current directory!
    echo Current directory: %CD%
    echo Please run this batch file from the project directory: d:\Morph-app
    pause
    exit /b 1
)
echo.
echo ========================================
echo   TEST COMPLETE
echo ========================================
echo.
pause
