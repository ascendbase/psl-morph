@echo off
echo ========================================
echo   CLOUDFLARE TUNNEL SETUP
echo ========================================
echo.

echo Step 1: Checking if cloudflared is installed...
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo cloudflared not found!
    echo Please install it first:
    echo 1. Download from: https://github.com/cloudflare/cloudflared/releases/latest
    echo 2. Download cloudflared-windows-amd64.exe
    echo 3. Rename to cloudflared.exe
    echo 4. Move to C:\cloudflared\
    echo 5. Add C:\cloudflared to your PATH
    echo.
    pause
    exit /b 1
)

echo cloudflared found!
cloudflared --version
echo.

echo Step 2: Login to Cloudflare (if not already logged in)...
echo This will open your browser for authentication
pause
cloudflared tunnel login

echo.
echo Step 3: Starting tunnel for ComfyUI...
echo This will create a public URL for your local ComfyUI
echo.

echo Starting tunnel on port 8188...
echo Keep this window open to maintain the tunnel!
echo.

cloudflared tunnel --url http://localhost:8188
