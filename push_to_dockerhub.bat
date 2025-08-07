@echo off
echo Tagging the image for Docker Hub...
docker tag ascendbase/face-morphing-comfyui:latest ascendbase/face-morphing-comfyui:latest

echo Pushing the image to Docker Hub...
docker push ascendbase/face-morphing-comfyui:latest

echo Image pushed successfully! You can now use this image with RunPod serverless.
echo The image address is: ascendbase/face-morphing-comfyui:latest
pause