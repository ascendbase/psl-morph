@echo off
echo Working Docker Build Script
echo ===========================
echo.

echo Current directory: %CD%
echo.

echo Available Dockerfiles:
dir Dockerfile*

echo.
echo Building with Dockerfile.runpod.fast (known to work)...
echo.

docker build -f Dockerfile.runpod.fast -t ascendbase/face-morphing-comfyui:latest .

echo.
echo Build completed! Check the output above for any errors.
echo.
echo Next steps:
echo 1. If build succeeded: run push_to_dockerhub.bat
echo 2. If build failed: try the alternative below
echo.
echo Alternative: Use the original Dockerfile.runpod
echo docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:latest .
echo.
pause
