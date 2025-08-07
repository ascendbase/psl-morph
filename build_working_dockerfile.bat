@echo off
echo ========================================
echo Building WORKING Dockerfile for RunPod
echo ========================================
echo.
echo This Dockerfile is based on your successful local test!
echo Key improvements:
echo - Python 3.12 (matches your working environment)
echo - ComfyUI Manager approach (proven to work)
echo - Exact dependencies from your successful log
echo - numpy^<2 constraint (critical!)
echo - Impact Pack install script execution
echo.
echo Building Docker image...
docker build -f Dockerfile.runpod.working -t ascendbase/face-morphing-comfyui:working .
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ BUILD SUCCESSFUL!
    echo.
    echo Next steps:
    echo 1. Test locally: docker run -p 8188:8188 ascendbase/face-morphing-comfyui:working
    echo 2. Push to Docker Hub: docker push ascendbase/face-morphing-comfyui:working
    echo 3. Update RunPod endpoint to use :working tag
) else (
    echo ❌ BUILD FAILED!
    echo Check the error messages above.
)
echo.
pause
