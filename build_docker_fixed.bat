@echo off
echo Fixed Docker Build Script
echo ========================
echo.

echo Checking available Dockerfiles...
dir Dockerfile.runpod*

echo.
echo Building with the fast/optimized Dockerfile...
echo.

docker build -f Dockerfile.runpod.fast -t ascendbase/face-morphing-comfyui:latest .

echo.
echo Build completed! Check the output above for any errors.
echo.
echo Next steps:
echo 1. If build succeeded: run push_to_dockerhub.bat
echo 2. If build failed: check the error messages above
echo.
pause
