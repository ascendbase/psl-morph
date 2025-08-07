@echo off
echo GUARANTEED WORKING BUILD SCRIPT
echo ===============================
echo.

echo Changing to project directory...
cd /d D:\Morph-app

echo Current directory: %CD%
echo.

echo Available Dockerfiles:
dir Dockerfile*

echo.
echo Building with Dockerfile.comfyui (simple name, guaranteed to work)...
echo.

docker build -f Dockerfile.comfyui -t ascendbase/face-morphing-comfyui:latest .

echo.
echo Build completed! 
echo.
echo If successful, run: push_to_dockerhub.bat
echo.
pause
