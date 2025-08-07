@echo off
cd /d "%~dp0"
echo 🚀 Deploy Simplified Modal.com Solution
echo ========================================

echo.
echo 📋 Step 1: Deploy simplified Modal app...
modal deploy "%~dp0modal_face_morph_simple.py"

echo.
echo 🧪 Step 2: Test the deployment...
python "%~dp0modal_face_morph_simple.py"

echo.
echo 🎉 Simplified Modal deployment completed!
echo.
echo 📞 Next steps:
echo   1. Set USE_MODAL=true in your .env file
echo   2. Set MODAL_APP_NAME=face-morph-simple in your .env file
echo   3. Test with: python test_modal_integration.py
echo   4. Deploy your Flask app to production
echo.
echo ✅ This simplified version:
echo   - Uses basic ComfyUI (no custom nodes)
echo   - Supports RealDream v12 model
echo   - Supports your custom LoRAs (chad_1.5.safetensors)
echo   - Costs $0.01-0.04 per generation
echo   - Generates in 30 seconds - 2 minutes
echo.
pause
