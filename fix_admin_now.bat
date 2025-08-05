@echo off
echo ========================================
echo   Fixing Admin Privileges
echo ========================================
echo.

echo Stopping any running app instances...
taskkill /f /im python.exe 2>nul

echo.
echo Running admin privilege fix...
python fix_admin_privileges.py

echo.
echo Fix completed! 
echo.
echo Now restart the app with: start_rtx5090.bat
echo Then login with: ascendbase@gmail.com / morphpas
echo You should see the Admin button in the dashboard.
echo.
pause