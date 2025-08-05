@echo off
echo ========================================
echo   Connect RunPod GPU to Face Morphing App
echo ========================================
echo.

echo Step 1: Testing if SSH tunnel is already working...
curl -s http://localhost:8188/system_stats >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ SSH tunnel already working!
    echo ✅ ComfyUI accessible at http://localhost:8188
    goto :run_app
)

echo ❌ SSH tunnel not working. Let's create it...
echo.

echo Step 2: Creating SSH tunnel to your RTX 5090...
echo Command: ssh root@149.36.1.79 -p 33805 -L 8188:localhost:8188 -N
echo.
echo IMPORTANT: 
echo - You'll need to enter your RunPod root password
echo - Find it in your RunPod dashboard under "Connection Details"
echo - Keep this window open after connecting!
echo.

pause
echo Starting SSH tunnel...
ssh root@149.36.1.79 -p 33805 -L 8188:localhost:8188 -N

:run_app
echo.
echo Step 3: SSH tunnel should be running!
echo Test it: Open browser → http://localhost:8188
echo.
echo Step 4: Ready to run your Face Morphing app!
echo Command: python app.py
echo.
pause

python app.py