@echo off
echo 🔥 Face Morphing Web App Startup Script
echo =====================================

echo.
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found

echo.
echo 📦 Installing dependencies...
echo Trying exact versions first...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Exact versions failed, trying flexible versions...
    pip install -r requirements-flexible.txt
    if errorlevel 1 (
        echo ⚠️  Flexible versions failed, trying individual packages...
        pip install Flask Pillow requests Werkzeug
        if errorlevel 1 (
            echo ❌ All dependency installation methods failed
            echo Please try manually: pip install Flask Pillow requests Werkzeug
            pause
            exit /b 1
        )
    )
)

echo ✅ Dependencies installed

echo.
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
echo ✅ Directories created

echo.
echo 🔍 Checking ComfyUI connection...
python -c "import requests; requests.get('http://127.0.0.1:8188/system_stats', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: Cannot connect to ComfyUI at http://127.0.0.1:8188
    echo Please make sure ComfyUI is running with API enabled:
    echo   python main.py --listen 127.0.0.1 --port 8188
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
) else (
    echo ✅ ComfyUI connection successful
)

echo.
echo 🚀 Starting Face Morphing Web App...
echo 🌐 Open http://localhost:5000 in your browser
echo 🛑 Press Ctrl+C to stop the server
echo.

python app.py

echo.
echo 👋 Face Morphing Web App stopped
pause