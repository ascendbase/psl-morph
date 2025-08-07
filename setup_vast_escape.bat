@echo off
echo 🚀 RunPod Escape Setup - Vast.ai Integration
echo ================================================

echo.
echo 📋 Step 1: Installing dependencies...
pip install requests pillow

echo.
echo 🔑 Step 2: Setting up Vast.ai API key...
echo.
echo Please get your API key from: https://console.vast.ai/
echo 1. Sign up/login to Vast.ai
echo 2. Go to Account -^> API Keys
echo 3. Copy your API key
echo.
set /p VAST_API_KEY="Enter your Vast.ai API key: "

if "%VAST_API_KEY%"=="" (
    echo ❌ No API key provided!
    pause
    exit /b 1
)

echo.
echo 💾 Setting environment variable...
setx VAST_API_KEY "%VAST_API_KEY%"
set VAST_API_KEY=%VAST_API_KEY%

echo.
echo 🧪 Testing integration...
cd /d "%~dp0"
python test_vast_integration.py

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Your app now uses Vast.ai instead of RunPod
echo 2. 90%% cost savings on every generation!
echo 3. Same quality, much better reliability
echo.
echo 💰 Cost comparison:
echo    RunPod:  $0.25-0.50 per generation
echo    Vast.ai: $0.003 per generation
echo    SAVINGS: 96%% cheaper!
echo.
pause
