@echo off
echo ========================================
echo    MODAL.COM COMPLETE SETUP SCRIPT
echo ========================================
echo.

echo Navigating to project directory...
cd /d "d:\Morph-app"
if not exist "modal_face_morph_simple.py" (
    echo ERROR: modal_face_morph_simple.py not found in d:\Morph-app
    echo Please make sure you're running this script from the correct location
    pause
    exit /b 1
)

echo Step 1: Installing Modal...
pip install modal
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Modal
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up Modal authentication...
echo This will open your browser to authenticate with Modal.com
echo Please complete the authentication process in your browser.
echo.
pause
modal token new

echo.
echo Step 3: Deploying Modal app...
echo Deploying face-morph-simple app to Modal.com...
echo Current directory: %cd%
echo Looking for: modal_face_morph_simple.py
dir modal_face_morph_simple.py
modal deploy modal_face_morph_simple.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to deploy Modal app
    echo Make sure modal_face_morph_simple.py exists in the current directory
    pause
    exit /b 1
)

echo.
echo Step 4: Verifying deployment...
modal app list

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Copy your Modal token to Railway environment variables
echo 2. Set USE_MODAL=true in Railway
echo 3. Set USE_CLOUD_GPU=false in Railway
echo 4. Redeploy your Railway app
echo.
echo Your Modal.com integration is ready!
echo Cost savings: 95%% vs RunPod
echo.
pause
