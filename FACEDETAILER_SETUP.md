# FaceDetailer Workflow Setup Guide

## Overview

The FaceDetailer workflow provides superior face detection and inpainting compared to ReActor face swapping. It uses advanced AI models to precisely detect faces and apply transformations while maintaining natural-looking results.

## Required Extensions

Before using the FaceDetailer workflow, ensure these ComfyUI extensions are installed:

### 1. ComfyUI-Impact-Pack
- **Purpose**: Provides FaceDetailer node and advanced face processing
- **Installation**: Via ComfyUI Manager or manual installation
- **Repository**: https://github.com/ltdrdata/ComfyUI-Impact-Pack

### 2. ComfyUI_UltralyticsDetectorProvider  
- **Purpose**: Provides YOLO-based face detection models
- **Installation**: Via ComfyUI Manager
- **Repository**: https://github.com/MrForExample/ComfyUI-3D-Pack

### 3. ComfyUI_Segment_Anything
- **Purpose**: Provides SAM (Segment Anything Model) for precise masking
- **Installation**: Via ComfyUI Manager
- **Repository**: https://github.com/storyicon/comfyui_segment_anything

## Required Models

The FaceDetailer workflow requires these models to be downloaded:

### Face Detection Model
- **File**: `face_yolov8m.pt`
- **Location**: `ComfyUI/models/ultralytics/bbox/`
- **Download**: Automatically downloaded when first used

### SAM Model
- **File**: `sam_vit_b_01ec64.pth`
- **Location**: `ComfyUI/models/sams/`
- **Download**: Automatically downloaded when first used

### Base Models (Already Required)
- **Checkpoint**: `real-dream-15.safetensors` in `ComfyUI/models/checkpoints/`
- **LoRA**: `chad_sd1.5.safetensors` in `ComfyUI/models/loras/`

## Installation Steps

### Step 1: Install Extensions
1. Open ComfyUI Manager (if installed) or install extensions manually
2. Search for and install:
   - ComfyUI-Impact-Pack
   - ComfyUI_UltralyticsDetectorProvider
   - ComfyUI_Segment_Anything
3. Restart ComfyUI after installation

### Step 2: Verify Installation
Run the test script to verify everything is working:

```bash
python test_facedetailer.py
```

### Step 3: Switch to FaceDetailer
The app is now configured to use FaceDetailer by default. If you need to switch back to ReActor, edit `config.py`:

```python
CURRENT_WORKFLOW = 'reactor'  # or 'facedetailer'
```

## Workflow Comparison

| Feature | ReActor | FaceDetailer |
|---------|---------|--------------|
| Face Detection | Basic | Advanced YOLO + SAM |
| Precision | Good | Excellent |
| Natural Results | Good | Superior |
| Speed | Fast | Moderate |
| Setup Complexity | Simple | Moderate |

## FaceDetailer Advantages

1. **Precise Face Detection**: Uses YOLO v8 for accurate face bounding boxes
2. **Advanced Masking**: SAM provides pixel-perfect face masks
3. **Natural Inpainting**: Better integration with surrounding areas
4. **Configurable Parameters**: Fine-tune detection thresholds and processing
5. **Multiple Face Support**: Can handle multiple faces in one image

## Troubleshooting

### Common Issues

#### 1. "FaceDetailer node not found"
- **Solution**: Install ComfyUI-Impact-Pack extension
- **Check**: Restart ComfyUI after installation

#### 2. "UltralyticsDetectorProvider not found"
- **Solution**: Install ComfyUI_UltralyticsDetectorProvider extension
- **Alternative**: Use built-in face detection models

#### 3. "SAM model not found"
- **Solution**: Install ComfyUI_Segment_Anything extension
- **Check**: Models will download automatically on first use

#### 4. "400 Bad Request" API Error
- **Solution**: Verify all extensions are properly installed
- **Check**: Run `test_facedetailer.py` to diagnose issues
- **Fallback**: Switch back to ReActor workflow temporarily

### Performance Optimization

#### For Better Speed:
- Use smaller SAM model: `sam_vit_b_01ec64.pth` (default)
- Reduce `guide_size` from 512 to 384
- Lower `max_size` from 1024 to 768

#### For Better Quality:
- Use larger SAM model: `sam_vit_h_4b8939.pth`
- Increase `guide_size` to 768
- Increase `max_size` to 1536
- Adjust `bbox_threshold` for better detection

## Configuration Parameters

The FaceDetailer workflow can be fine-tuned by modifying these parameters in the workflow JSON:

```json
{
  "guide_size": 512,           // Processing resolution
  "max_size": 1024,           // Maximum output size
  "bbox_threshold": 0.50,     // Face detection confidence
  "bbox_dilation": 10,        // Face box expansion
  "sam_threshold": 0.93,      // SAM segmentation threshold
  "feather": 5,               // Mask edge softening
  "denoise": 0.50             // Transformation strength (controlled by presets)
}
```

## Testing the Setup

### Manual Test in ComfyUI:
1. Load the FaceDetailer workflow in ComfyUI
2. Upload a test image
3. Queue the workflow
4. Verify it processes without errors

### API Test:
```bash
python test_facedetailer.py
```

### Web App Test:
1. Start the web app: `python app.py`
2. Upload an image
3. Select a preset (HTN/Chadlite/Chad)
4. Process and verify results

## Switching Between Workflows

You can easily switch between different workflows by editing `config.py`:

```python
# Available options:
CURRENT_WORKFLOW = 'facedetailer'  # Recommended
CURRENT_WORKFLOW = 'reactor'       # Fallback
CURRENT_WORKFLOW = 'inpaint'       # Alternative
```

## Support

If you encounter issues:

1. **Check Extensions**: Ensure all required extensions are installed
2. **Verify Models**: Confirm models are downloaded and in correct locations
3. **Test Manually**: Try the workflow in ComfyUI interface first
4. **Check Logs**: Review ComfyUI console output for error messages
5. **Fallback**: Switch to ReActor workflow if needed

The FaceDetailer workflow provides superior results but requires additional setup. Once configured properly, it delivers more natural and precise face transformations than the ReActor approach.