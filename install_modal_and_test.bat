@echo off
cd /d "%~dp0"
echo 🔧 Installing Modal.com Package and Testing
echo ==========================================

echo.
echo 📦 Step 1: Installing Modal package...
pip install modal

echo.
echo 🧪 Step 2: Testing Modal integration...
python test_modal_integration.py

echo.
echo 🎉 Installation and testing completed!
echo.
echo 📞 If tests pass, your Modal.com solution is ready!
echo   - Modal app is deployed and working
echo   - Local environment is configured
echo   - Ready for production use
echo.
pause
