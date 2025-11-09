@echo off
echo ========================================
echo   DEPLOYING LOCAL COMFYUI FIX TO RAILWAY
echo ========================================
echo.

echo This will push the local ComfyUI connection fixes to Railway.
echo.
echo Files being deployed:
echo  - local_comfyui_client.py (main fix)
echo  - cloudflare_tunnel_detector.py (tunnel detection)
echo  - tunnel_registry.py (URL storage)
echo  - app.py (webhook integration)
echo.

set /p confirm="Continue with deployment? (y/n): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Adding files to git...
git add local_comfyui_client.py
git add cloudflare_tunnel_detector.py
git add tunnel_registry.py
git add app.py

echo.
echo Step 2: Committing changes...
git commit -m "Fix: Enable Railway app to connect to local ComfyUI via tunnel

- Updated LocalComfyUIClient to use dynamic tunnel URL detection
- Added tunnel detection and registry system
- Fixed connection issue from localhost:8188 to tunnel URLs
- Enables local GPU usage for face transformations"

echo.
echo Step 3: Pushing to Railway...
git push origin main

echo.
echo ========================================
echo   DEPLOYMENT COMPLETE
echo ========================================
echo.
echo Your Railway app should now be able to connect to your local ComfyUI!
echo.
echo Next steps:
echo 1. Wait for Railway deployment to complete (check Railway dashboard)
echo 2. Run: .\start_production_cloudflare.bat
echo 3. Test with: python test_tunnel_connection_fix.py
echo 4. Try the web app with real image uploads
echo.
pause
