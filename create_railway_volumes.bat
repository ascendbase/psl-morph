@echo off
echo ========================================
echo Railway Facial Evaluation Volume Setup
echo ========================================
echo.

echo Creating Railway volume for facial evaluation images...
echo.

echo Step 1: Creating 'facial-evaluations' volume...
railway volume create facial-evaluations --mount-path /app/facial_evaluations --size 1GB
if %errorlevel% neq 0 (
    echo ERROR: Failed to create facial-evaluations volume
    echo Try creating it manually in Railway dashboard
    pause
    exit /b 1
)
echo ✅ facial-evaluations volume created successfully
echo.

echo Step 2: Listing all volumes...
railway volume list
echo.

echo ========================================
echo Facial Evaluation Volume Ready! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Deploy your app: railway up
echo 2. Test facial evaluation feature
echo 3. Check admin dashboard: /admin/facial-evaluations
echo.
echo Your facial evaluation images will now persist!
echo.
pause
