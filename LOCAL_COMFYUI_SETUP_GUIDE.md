# Local ComfyUI Setup Guide

This guide will help you configure your Face Morph app to use your local ComfyUI instead of cloud GPU services.

## ✅ What's Been Done

Your app has been successfully modified to support local ComfyUI:

1. **New Local ComfyUI Client** (`local_comfyui_client.py`)
   - Loads your specific workflow: `comfyui_workflows/workflow_facedetailer.json`
   - Handles image upload, processing, and result retrieval
   - Includes proper error handling and logging

2. **Updated Configuration** (`config.py`)
   - `USE_LOCAL_COMFYUI = true` (enabled)
   - `USE_MODAL = false` (disabled)
   - `USE_CLOUD_GPU = false` (disabled)
   - Points to your workflow file

3. **Updated Main App** (`app.py`)
   - Now prioritizes local ComfyUI when enabled
   - Uses your specific workflow for face transformations
   - Maintains all existing features (auth, payments, etc.)

4. **Test Script** (`test_local_comfyui.py`)
   - Comprehensive testing of the local ComfyUI integration
   - Verifies connection, workflow loading, and generation

5. **Easy Startup** (`start_with_local_comfyui.bat`)
   - One-click startup with proper configuration
   - Tests ComfyUI connection before starting the app

## 🚀 How to Use

### Step 1: Start ComfyUI
Make sure your ComfyUI is running on `http://127.0.0.1:8188` with the following requirements:

**Required Models:**
- `real-dream-15.safetensors` (checkpoint)
- `chad_sd1.5.safetensors` (LoRA)

**Required Nodes:**
- FaceDetailer (Impact Pack)
- UltralyticsDetectorProvider
- SAMLoader
- Standard ComfyUI nodes

### Step 2: Test the Integration
Run the test script to verify everything works:
```bash
python test_local_comfyui.py
```

### Step 3: Start Your App
Use the provided batch file:
```bash
start_with_local_comfyui.bat
```

Or start manually:
```bash
python app.py
```

### Step 4: Use the App
1. Open `http://localhost:5000` in your browser
2. Upload an image
3. Click "Start Transformation"
4. Your local GPU will process the image using the FaceDetailer workflow!

## 🔧 Configuration Options

You can customize the setup by modifying `config.py`:

```python
# Local ComfyUI Configuration
USE_LOCAL_COMFYUI = True  # Enable/disable local ComfyUI
COMFYUI_URL = "http://127.0.0.1:8188"  # ComfyUI server URL
LOCAL_COMFYUI_WORKFLOW = "comfyui_workflows/workflow_facedetailer.json"  # Workflow file
COMFYUI_TIMEOUT = 300  # Timeout in seconds
```

## 📁 Workflow Details

The app uses your `workflow_facedetailer.json` which includes:

- **Node 1**: CheckpointLoaderSimple (real-dream-15.safetensors)
- **Node 2**: LoraLoader (chad_sd1.5.safetensors)
- **Node 3**: CLIP Text Encode (Positive prompt)
- **Node 4**: CLIP Text Encode (Negative prompt)
- **Node 5**: LoadImage (User's uploaded image)
- **Node 6**: UltralyticsDetectorProvider (Face detection)
- **Node 7**: SAMLoader (Segmentation)
- **Node 8**: FaceDetailer (Main processing)
- **Node 9**: SaveImage (Output)

## 🎛️ How It Works

1. **User uploads image** → Saved to `uploads/` folder
2. **Image uploaded to ComfyUI** → Via `/upload/image` API
3. **Workflow prepared** → Your workflow with user's image and settings
4. **Generation started** → Queued in ComfyUI with unique prompt ID
5. **Status monitoring** → App polls ComfyUI for completion
6. **Result retrieved** → Downloaded and saved to `outputs/` folder
7. **User downloads result** → Served through the web interface

## 🔍 Troubleshooting

### ComfyUI Connection Issues
- Ensure ComfyUI is running on `http://127.0.0.1:8188`
- Check that ComfyUI API is enabled (default port 8188)
- Verify no firewall is blocking the connection

### Missing Models/Nodes
- Install Impact Pack for FaceDetailer
- Download required models to ComfyUI's models folder
- Check ComfyUI console for missing node errors

### Workflow Issues
- Verify `comfyui_workflows/workflow_facedetailer.json` exists
- Check that all nodes in the workflow are available
- Test the workflow manually in ComfyUI first

### Generation Failures
- Check ComfyUI console for error messages
- Verify uploaded image is valid
- Ensure sufficient GPU memory is available

## 📊 Performance Benefits

Using local ComfyUI provides:

- **No cloud costs** - Use your own GPU for free
- **Faster processing** - No network latency
- **Full control** - Customize models and settings
- **Privacy** - Images never leave your machine
- **Reliability** - No dependency on external services

## 🔄 Switching Back to Cloud

If you want to switch back to cloud GPU services, simply modify `config.py`:

```python
USE_LOCAL_COMFYUI = False
USE_MODAL = True  # or USE_CLOUD_GPU = True
```

## 📝 Logs and Monitoring

The app provides detailed logging:
- ComfyUI connection status
- Workflow preparation details
- Generation progress
- Error messages and troubleshooting info

Check the console output when running the app for real-time status updates.

## 🎉 Success!

Your Face Morph app now uses your local ComfyUI with the FaceDetailer workflow! Users can upload images and get high-quality face transformations processed entirely on your local GPU.

The app maintains all its existing features:
- User authentication
- Credit system
- Payment processing
- Admin dashboard
- Generation history

But now it's powered by your local hardware instead of expensive cloud services!
