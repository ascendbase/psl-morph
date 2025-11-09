@echo off
REM Build and Push ComfyUI Docker Image for RunPod
REM This script builds the Docker image with Impact Pack pre-installed

REM Change to the directory where this script is located
cd /d "%~dp0"

echo ================================================
echo Building ComfyUI Docker Image for RunPod
echo ================================================
echo.
echo Working directory: %CD%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Get DockerHub username
set /p DOCKERHUB_USERNAME="Enter your DockerHub username: "

if "%DOCKERHUB_USERNAME%"=="" (
    echo ERROR: DockerHub username cannot be empty!
    pause
    exit /b 1
)

echo.
echo Building Docker image...
echo This will take 15-30 minutes on first build.
echo.

REM Check if Dockerfile exists
if not exist "Dockerfile.runpod.comfyui" (
    echo ERROR: Dockerfile.runpod.comfyui not found!
    echo.
    echo Please make sure you are running this script from the project root directory:
    echo d:\Morph-app
    echo.
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo ✓ Found Dockerfile.runpod.comfyui
echo.

REM Build the Docker image
docker build -f Dockerfile.runpod.comfyui -t %DOCKERHUB_USERNAME%/comfyui-morph:latest .

if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build successful!
echo ================================================
echo.
echo Image: %DOCKERHUB_USERNAME%/comfyui-morph:latest
echo Size: 
docker images %DOCKERHUB_USERNAME%/comfyui-morph:latest
echo.

REM Ask if user wants to push to DockerHub
set /p PUSH="Do you want to push to DockerHub? (y/n): "

if /i "%PUSH%"=="y" (
    echo.
    echo Logging into DockerHub...
    echo Please enter your DockerHub credentials when prompted.
    echo.
    
    docker login
    
    if errorlevel 1 (
        echo.
        echo ERROR: Docker login failed!
        pause
        exit /b 1
    )
    
    echo.
    echo Pushing image to DockerHub...
    echo This may take 10-20 minutes depending on your internet speed.
    echo.
    
    docker push %DOCKERHUB_USERNAME%/comfyui-morph:latest
    
    if errorlevel 1 (
        echo.
        echo ERROR: Docker push failed!
        pause
        exit /b 1
    )
    
    echo.
    echo ================================================
    echo SUCCESS! Image pushed to DockerHub
    echo ================================================
    echo.
    echo Your image is now available at:
    echo https://hub.docker.com/r/%DOCKERHUB_USERNAME%/comfyui-morph
    echo.
    echo Next steps:
    echo 1. Go to https://www.runpod.io/console/serverless
    echo 2. Create a new endpoint
    echo 3. Use image: %DOCKERHUB_USERNAME%/comfyui-morph:latest
    echo.
) else (
    echo.
    echo Image built but not pushed to DockerHub.
    echo You can test it locally with:
    echo docker run -p 8188:8188 %DOCKERHUB_USERNAME%/comfyui-morph:latest
    echo.
)

echo.
echo IMPORTANT: Save this image name for RunPod:
echo %DOCKERHUB_USERNAME%/comfyui-morph:latest
echo.

pause
