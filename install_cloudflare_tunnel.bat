@echo off
echo ========================================
echo   CLOUDFLARE TUNNEL INSTALLATION
echo ========================================
echo.

echo Step 1: Downloading Cloudflare Tunnel...
echo.

REM Create cloudflared directory
if not exist "C:\cloudflared" mkdir "C:\cloudflared"

echo Downloading cloudflared for Windows...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'C:\cloudflared\cloudflared.exe'"

if exist "C:\cloudflared\cloudflared.exe" (
    echo ✅ Download successful!
) else (
    echo ❌ Download failed. Please download manually from:
    echo https://github.com/cloudflare/cloudflared/releases/latest
    echo Download: cloudflared-windows-amd64.exe
    echo Save to: C:\cloudflared\cloudflared.exe
    pause
    exit /b 1
)

echo.
echo Step 2: Adding to PATH...

REM Add to PATH for current session
set PATH=%PATH%;C:\cloudflared

REM Add to system PATH permanently
powershell -Command "if (-not ($env:PATH -like '*C:\cloudflared*')) { [Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\cloudflared', 'Machine') }"

echo.
echo Step 3: Testing installation...
C:\cloudflared\cloudflared.exe --version

if %ERRORLEVEL% EQU 0 (
    echo ✅ Cloudflare Tunnel installed successfully!
) else (
    echo ❌ Installation verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo Cloudflare Tunnel is now installed and ready to use.
echo.
echo Next steps:
echo 1. Close and reopen your terminal (to refresh PATH)
echo 2. Run: start_production_cloudflare.bat
echo 3. Your Railway app will automatically detect the tunnel!
echo.

pause
