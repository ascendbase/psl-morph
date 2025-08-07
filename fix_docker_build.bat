@echo off
echo Docker Build Recovery Tool
echo =========================
echo.
echo Current build appears stuck. Let's fix this...
echo.

echo 1. Stopping any stuck Docker processes...
docker system prune -f

echo.
echo 2. Checking Docker status...
docker version

echo.
echo 3. Killing any stuck build processes...
for /f "tokens=1" %%i in ('docker ps -q') do docker kill %%i 2>nul

echo.
echo 4. Cleaning up build cache...
docker builder prune -f

echo.
echo 5. Ready to restart build with optimized Dockerfile...
echo.
echo Next steps:
echo - Press Ctrl+C in the original build terminal to stop it
echo - Run: docker build -f Dockerfile.runpod.optimized -t ascendbase/face-morphing-comfyui:latest .
echo.
pause
