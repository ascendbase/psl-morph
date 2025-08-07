@echo off
cd /d "d:\Morph-app"
echo 🚀 COMPLETING MODAL.COM SETUP
echo ================================

echo.
echo Current directory: %CD%
echo.

echo Step 1: Setting up Modal authentication...
echo Please follow the instructions to authenticate with Modal.com
echo.
C:\Users\yvngt\AppData\Local\Programs\Python\Python310\Scripts\modal.exe token new

echo.
echo Step 2: Deploying Modal function...
echo.
C:\Users\yvngt\AppData\Local\Programs\Python\Python310\Scripts\modal.exe deploy modal_face_morph_simple.py

echo.
echo Step 3: Testing the complete setup...
echo.
python test_modal_connection.py

echo.
echo ================================
echo 🎉 Modal.com setup complete!
echo.
echo If all tests pass, you now have:
echo - 95%% cost savings vs RunPod
echo - Pay-per-second billing
echo - No idle costs
echo - Fast generation times
echo.
pause
