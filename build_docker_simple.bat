@echo off
echo Simple Docker Build Script
echo ==========================
echo.

echo Building with the updated Dockerfile.runpod...
echo This version has optimizations to prevent hanging.
echo.

docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:latest .

echo.
echo Build completed! Check the output above for any errors.
echo.
echo Next steps:
echo 1. If build succeeded: run push_to_dockerhub.bat
echo 2. If build failed: check the error messages above
echo.
pause
