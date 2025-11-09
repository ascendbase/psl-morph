# FaceDetailer Precision Tuning Guide for Feature-Specific Workflows

## 🎯 Problem: Inaccurate Feature Targeting

When using FaceDetailer for specific facial features, it often affects surrounding areas instead of just the target feature. This happens because FaceDetailer has several parameters that control the detection area, processing region, and blending behavior.

## 🔧 Key FaceDetailer Parameters to Adjust

### **1. Detection Model Parameters**
```
bbox_detector: Controls which face detection model to use
- Use more precise models for better feature isolation
- Options: "bbox/face_yolov8n.pt", "bbox/face_yolov8s.pt", "bbox/face_yolov8m.pt"
- Recommendation: face_yolov8m.pt for better precision
```

### **2. Segmentation Parameters**
```
seg_detector: Controls segmentation precision
- "sam_vit_b_01ec64.pth" - Basic segmentation
- "sam_vit_l_0b3195.pth" - Better precision
- "sam_vit_h_4b8939.pth" - Highest precision (recommended for features)
```

### **3. Detection Threshold**
```
bbox_threshold: Controls detection sensitivity (0.1 - 1.0)
- Lower values = more sensitive detection
- Higher values = stricter detection
- Recommendation for features: 0.7-0.9 for precise targeting
```

### **4. Dilation Parameters**
```
bbox_dilation: Expands the detection box (pixels)
- Controls how much area around the detected feature is included
- Lower values = more precise targeting
- Recommendation: 
  - Eyes: 5-10 pixels
  - Nose: 8-15 pixels  
  - Lips: 5-12 pixels
  - Eyebrows: 3-8 pixels
  - Jaw: 15-25 pixels
  - Chin: 10-20 pixels
```

### **5. Crop Factor**
```
crop_factor: Controls the processing area size (1.0 - 3.0)
- 1.0 = tight crop around feature
- 3.0 = large area around feature
- Recommendation for precise features: 1.1-1.5
```

### **6. Drop Size**
```
drop_size: Minimum detection size to process
- Filters out small detections
- Recommendation: 10-50 depending on feature size
```

### **7. Feather and Blur Parameters**
```
feather: Edge blending amount (0-100)
- Controls how smoothly the processed area blends
- Lower = sharper edges, higher = smoother blending
- Recommendation: 5-15 for features

blur: Additional blur for blending (0.0-3.0)
- Extra smoothing for seamless integration
- Recommendation: 0.5-1.5 for features
```

## 🎨 Feature-Specific Optimal Settings

### **👁️ Eyes Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth", 
  "bbox_threshold": 0.8,
  "bbox_dilation": 8,
  "crop_factor": 1.2,
  "drop_size": 20,
  "feather": 8,
  "blur": 0.8,
  "guide_size": 384,
  "guide_size_for": true,
  "max_size": 1024
}
```

### **👃 Nose Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth",
  "bbox_threshold": 0.75,
  "bbox_dilation": 12,
  "crop_factor": 1.3,
  "drop_size": 25,
  "feather": 10,
  "blur": 1.0,
  "guide_size": 384,
  "guide_size_for": true,
  "max_size": 1024
}
```

### **👄 Lips Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth",
  "bbox_threshold": 0.85,
  "bbox_dilation": 6,
  "crop_factor": 1.15,
  "drop_size": 15,
  "feather": 6,
  "blur": 0.6,
  "guide_size": 384,
  "guide_size_for": true,
  "max_size": 1024
}
```

### **🤨 Eyebrows Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth",
  "bbox_threshold": 0.9,
  "bbox_dilation": 4,
  "crop_factor": 1.1,
  "drop_size": 10,
  "feather": 5,
  "blur": 0.4,
  "guide_size": 384,
  "guide_size_for": true,
  "max_size": 1024
}
```

### **🦴 Jaw Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth",
  "bbox_threshold": 0.7,
  "bbox_dilation": 20,
  "crop_factor": 1.4,
  "drop_size": 40,
  "feather": 15,
  "blur": 1.2,
  "guide_size": 512,
  "guide_size_for": true,
  "max_size": 1024
}
```

### **🫵 Chin Workflow Settings**
```json
{
  "bbox_detector": "bbox/face_yolov8m.pt",
  "seg_detector": "sam_vit_h_4b8939.pth",
  "bbox_threshold": 0.75,
  "bbox_dilation": 15,
  "crop_factor": 1.25,
  "drop_size": 30,
  "feather": 12,
  "blur": 1.0,
  "guide_size": 384,
  "guide_size_for": true,
  "max_size": 1024
}
```

## 🧪 Manual Testing Process

### **Step 1: Set Up Test Environment**
1. Open ComfyUI with your feature workflow
2. Load a test image with clear facial features
3. Connect a preview node to see intermediate results

### **Step 2: Test Detection Accuracy**
1. Start with `bbox_threshold = 0.5`
2. Gradually increase to 0.9 until only target feature is detected
3. Use ComfyUI's preview to verify detection boxes

### **Step 3: Fine-Tune Processing Area**
1. Adjust `bbox_dilation` starting from 0
2. Increase gradually until you get the right coverage
3. Monitor that surrounding features aren't included

### **Step 4: Optimize Crop Factor**
1. Start with `crop_factor = 1.0`
2. Increase slowly to 1.5 maximum
3. Find balance between context and precision

### **Step 5: Perfect the Blending**
1. Adjust `feather` for edge smoothness
2. Tune `blur` for seamless integration
3. Test with different face angles and lighting

## 🔍 Debugging Tools in ComfyUI

### **Preview Nodes to Add:**
```
1. PreviewImage after bbox detection
2. PreviewImage after segmentation  
3. PreviewImage after crop
4. PreviewImage after processing
5. PreviewImage final result
```

### **What to Look For:**
- ✅ Detection box only covers target feature
- ✅ No overlap with adjacent features
- ✅ Smooth blending at edges
- ✅ Natural-looking result
- ❌ Artifacts in surrounding areas
- ❌ Harsh edges or visible seams

## 📊 Testing Matrix

Create a test matrix for each feature:

| Parameter | Min Value | Max Value | Optimal Range | Notes |
|-----------|-----------|-----------|---------------|-------|
| bbox_threshold | 0.1 | 1.0 | 0.7-0.9 | Higher = more precise |
| bbox_dilation | 0 | 50 | 5-25 | Feature dependent |
| crop_factor | 1.0 | 3.0 | 1.1-1.5 | Lower = more precise |
| feather | 0 | 100 | 5-15 | Balance smoothness |
| blur | 0.0 | 3.0 | 0.4-1.5 | Subtle blending |

## 🎯 Advanced Techniques

### **Custom Segmentation Masks**
- Use ControlNet with segmentation maps
- Create manual masks for ultra-precise control
- Combine multiple detection methods

### **Multi-Stage Processing**
- First pass: rough feature detection
- Second pass: refined processing with tight parameters
- Third pass: blending and cleanup

### **Conditional Processing**
- Use different parameters based on face size
- Adjust settings for different face angles
- Adapt to lighting conditions

## 🚀 Quick Start Testing Script

Create this test workflow in ComfyUI:

```
1. Load Image
2. FaceDetailer (with test parameters)
3. Preview (to see detection)
4. Save Image (for comparison)
5. Repeat with different parameters
```

## 📈 Optimization Workflow

1. **Start Conservative**: High thresholds, low dilation
2. **Test Incrementally**: Change one parameter at a time
3. **Document Results**: Keep notes on what works
4. **Create Presets**: Save optimal settings for each feature
5. **Validate Across Images**: Test with different faces

## 🎨 Expected Results

After proper tuning, you should achieve:
- ✅ **Eyes**: Only eye shape/size changes, eyebrows untouched
- ✅ **Nose**: Only nose modification, lips/cheeks unchanged  
- ✅ **Lips**: Only lip enhancement, nose/chin unaffected
- ✅ **Eyebrows**: Only brow shape, eyes/forehead unchanged
- ✅ **Jaw**: Only jawline, neck/cheeks minimally affected
- ✅ **Chin**: Only chin area, lips/jaw mostly preserved

The key is finding the sweet spot where the feature is properly detected and processed without affecting surrounding areas!
