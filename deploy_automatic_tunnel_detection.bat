@echo off
echo ========================================
echo   Deploying Automatic Tunnel Detection
echo ========================================
echo.

echo Deploying directly to Railway...
railway up

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo IMPORTANT: You can now delete the COMFYUI_URL environment variable from Railway!
echo.
echo The app will automatically:
echo - Detect your running Cloudflare tunnel
echo - Connect to the current tunnel URL
echo - Fall back to local ComfyUI if no tunnel found
echo.
echo No more manual URL updates needed when tunnel restarts!
echo.
pause
