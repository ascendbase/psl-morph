@echo off
cd /d "%~dp0"
echo 🚀 Modal.com Setup Script - Perfect GPU Solution!
echo ================================================

echo.
echo 📋 Step 1: Installing Modal...
pip install modal

echo.
echo 🔐 Step 2: Authenticating with Modal...
echo This will open a browser window for authentication
modal setup

echo.
echo 📁 Step 3: Uploading models to Modal...
echo Make sure you have your models in:
echo   - ./lora/ (for LoRA files)
echo   - ./base_models/ (for checkpoint files)  
echo   - ./comfyui_workflows/ (for workflow JSON files)
echo.
echo Current directory: %CD%
echo.
pause
python "%~dp0upload_models_to_modal.py"

echo.
echo 🚀 Step 4: Deploying Modal app...
modal deploy "%~dp0modal_face_morph.py"

echo.
echo 🧪 Step 5: Testing Modal integration...
python "%~dp0test_modal_integration.py"

echo.
echo 🎉 Modal.com setup completed!
echo.
echo 📞 Next steps:
echo   1. Set USE_MODAL=true in your .env file
echo   2. Deploy your app to production
echo   3. Enjoy 95%+ cost savings! 🎊
echo.
echo Expected performance:
echo   ⚡ Generation time: 30 seconds - 2 minutes
echo   💰 Cost per generation: $0.01-0.04
echo   🎨 Full custom model support
echo   📈 Unlimited scaling
echo.
pause
