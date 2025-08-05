@echo off
echo ========================================
echo   Test Face Morphing App Locally
echo ========================================
echo.

echo This will run your app in LOCAL MODE for testing
echo (without RunPod GPU - just to test the interface)
echo.

echo Step 1: Switching to local ComfyUI mode...
echo Updating .env file...

echo # Face Morphing App - Local Test Configuration > .env.local
echo # This runs without RunPod for testing the interface >> .env.local
echo. >> .env.local
echo # Disable cloud GPU for local testing >> .env.local
echo USE_CLOUD_GPU=false >> .env.local
echo USE_RUNPOD_POD=false >> .env.local
echo. >> .env.local
echo # Local ComfyUI (if you have it installed) >> .env.local
echo COMFYUI_URL=http://127.0.0.1:8188 >> .env.local
echo COMFYUI_TIMEOUT=300 >> .env.local
echo. >> .env.local
echo # Application settings >> .env.local
echo SECRET_KEY=your_very_secure_secret_key_here_change_this >> .env.local
echo DEBUG=true >> .env.local
echo HOST=0.0.0.0 >> .env.local
echo PORT=5000 >> .env.local
echo. >> .env.local
echo # Database >> .env.local
echo DATABASE_URL=sqlite:///face_morph.db >> .env.local
echo. >> .env.local
echo # Security >> .env.local
echo LOGIN_DISABLED=false >> .env.local
echo SECURE_FILENAME_ENABLED=true >> .env.local
echo MAX_CONTENT_LENGTH=16777216 >> .env.local

copy .env.local .env

echo ✅ Configured for local testing
echo.

echo Step 2: Starting your Face Morphing SaaS app...
echo.
echo Your app will run at: http://localhost:5000
echo.
echo Features you can test:
echo ✅ User registration/login
echo ✅ Credit system
echo ✅ Payment interface
echo ✅ Admin panel (admin@example.com / admin123)
echo ✅ File upload interface
echo ❌ Actual image generation (needs GPU connection)
echo.

pause
python app.py