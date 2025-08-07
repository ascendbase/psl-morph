@echo off
echo Restarting Docker Build with Optimized Dockerfile
echo ================================================
echo.

echo Step 1: Cleaning up previous build...
echo.
docker system prune -f
docker builder prune -f

echo.
echo Step 2: Starting optimized build...
echo This should be faster and more reliable!
echo.

echo Building with: Dockerfile.runpod.optimized
echo Image tag: ascendbase/face-morphing-comfyui:latest
echo.

docker build -f Dockerfile.runpod.optimized -t ascendbase/face-morphing-comfyui:latest .

echo.
echo Build completed! Check the output above for any errors.
echo.
echo Next steps:
echo 1. If build succeeded: run push_to_dockerhub.bat
echo 2. If build failed: check the error messages above
echo.
pause
