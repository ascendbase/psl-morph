@echo off
echo Starting FREE Face Morphing Production
echo ====================================

echo 1. Starting ComfyUI...
start "ComfyUI" cmd /k "cd /d D:\ComfyUI_windows_portable\ComfyUI && python main.py --listen 0.0.0.0 --port 8188"

timeout /t 10

echo 2. Choose your FREE tunnel:
echo [1] Cloudflare Tunnel (recommended)
echo [2] LocalTunnel
echo [3] Serveo
echo [4] Pinggy

set /p choice="Enter choice (1-4): "

if %choice%==1 (
    echo Starting Cloudflare Tunnel...
    start "Cloudflare" cmd /k "cloudflared tunnel run face-morph-gpu"
)
if %choice%==2 (
    echo Starting LocalTunnel...
    start "LocalTunnel" cmd /k "lt --port 8188 --subdomain face-morph-gpu"
)
if %choice%==3 (
    echo Starting Serveo...
    start "Serveo" cmd /k "ssh -R 80:localhost:8188 serveo.net"
)
if %choice%==4 (
    echo Starting Pinggy...
    start "Pinggy" cmd /k "ssh -p 443 -R0:localhost:8188 a.pinggy.io"
)

echo.
echo FREE Production setup complete!
echo Your local GPU is now accessible to your web app
pause