@echo off
echo.
echo ========================================
echo   BUILDING CUSTOM DOCKER IMAGE
echo ========================================
echo.
echo This will build your custom Docker image with:
echo   - Real Dream base model (SD1.5)
echo   - Chad LoRA model
echo   - ComfyUI setup
echo.
echo Building image: ascendbase/face-morphing-comfyui:latest
echo.
pause

echo Building Docker image...
docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:latest .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Docker build completed successfully!
echo.
echo ========================================
echo   PUSHING TO DOCKER HUB
echo ========================================
echo.
echo Pushing to Docker Hub...
echo Make sure you're logged in: docker login
echo.
pause

docker push ascendbase/face-morphing-comfyui:latest

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker push failed!
    echo You may need to login first: docker login
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS! Image pushed to Docker Hub
echo.
echo Your custom image is now available at:
echo   ascendbase/face-morphing-comfyui:latest
echo.
echo Next steps:
echo 1. Update your RunPod endpoint to use this image
echo 2. Wait for endpoint to restart
echo 3. Test with your models
echo.
pause
