@echo off
echo Docker Build Progress Monitor
echo ============================
echo.
echo Current build status:
docker images | findstr ascendbase/face-morphing-comfyui
echo.
echo If the image appears above, the build is complete!
echo If not, the build is still in progress.
echo.
echo Next steps after build completion:
echo 1. Log in to Docker Hub: docker login
echo 2. Push the image: push_to_dockerhub.bat
echo 3. Deploy to RunPod using RUNPOD_DEPLOYMENT_INSTRUCTIONS.md
echo.
pause
