@echo off
echo ========================================
echo Testing FaceDetailer Workflow
echo ========================================
echo.
echo After installing Impact Pack with any method:
echo.
echo 1. Start ComfyUI
echo 2. Go to http://localhost:8188
echo 3. Load workflow: comfyui_workflows/workflow_facedetailer.json
echo 4. Upload a test image (with a face)
echo 5. Click "Queue Prompt"
echo 6. Check for these nodes working:
echo    - UltralyticsDetectorProvider
echo    - SAMLoader  
echo    - FaceDetailer
echo.
echo SUCCESS INDICATORS:
echo ✅ No red error nodes
echo ✅ Workflow runs without crashes
echo ✅ Face detection and enhancement works
echo.
echo FAILURE INDICATORS:
echo ❌ Red error nodes
echo ❌ "Node not found" errors
echo ❌ Import/dependency errors in console
echo.
echo Press any key to continue...
pause
