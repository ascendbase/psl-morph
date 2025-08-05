@echo off
echo RunPod SSH Tunnel Setup
echo ========================

echo Setting up SSH tunnel to RunPod ComfyUI...
echo Tunnel: localhost:8188 -> 149.36.1.79:8188 (via SSH port 33805)
echo.

echo Starting SSH tunnel...
echo Note: You may need to enter your SSH password
echo.

ssh -L 8188:localhost:8188 -p 33805 root@149.36.1.79 -N -o StrictHostKeyChecking=no

echo.
echo SSH tunnel closed.
pause