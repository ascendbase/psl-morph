@echo off
REM Script to build and push the FIXED Docker image with all dependencies
REM This fixes the cv2 and numba import errors in RunPod serverless

echo 🔧 Building FIXED Docker image with all dependencies...
echo This will include: opencv-python-headless, numba, scipy, and more

REM Build the Docker image with fixed dependencies
echo Building Docker image...
docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:fixed .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
    
    echo 🚀 Pushing to Docker Hub...
    docker push ascendbase/face-morphing-comfyui:fixed
    
    if %errorlevel% equ 0 (
        echo ✅ Image pushed successfully!
        echo.
        echo 🎯 NEXT STEPS:
        echo 1. Go to RunPod Console → Serverless → Your Endpoint
        echo 2. Click 'Edit'
        echo 3. Update Container Image to: ascendbase/face-morphing-comfyui:fixed
        echo 4. Save Changes
        echo.
        echo This will fix all the cv2 and numba import errors!
    ) else (
        echo ❌ Failed to push image to Docker Hub
        echo Make sure you're logged in: docker login
    )
) else (
    echo ❌ Failed to build Docker image
    echo Check the Dockerfile.runpod for errors
)

pause
