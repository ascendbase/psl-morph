# ComfyUI FaceAnalysis Extension Setup Guide

## 🎯 What is ComfyUI_FaceAnalysis?

ComfyUI_FaceAnalysis is the **SOLUTION** we've been looking for! Unlike FaceDetailer which processes the entire face, this extension can target **specific facial features** like:

- ✅ **Eyes only**
- ✅ **Eyebrows only** 
- ✅ **Nose only**
- ✅ **Lips only**
- ✅ **Jaw/chin only**
- ✅ **Any combination** of features

## 🔧 Installation Steps

### **Step 1: Install the Extension**

**Option A: ComfyUI Manager (Recommended)**
1. Open ComfyUI in your browser
2. Click **"Manager"** button
3. Search for **"ComfyUI_FaceAnalysis"**
4. Click **"Install"**
5. Restart ComfyUI

**Option B: Manual Installation**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cubiq/ComfyUI_FaceAnalysis.git
cd ComfyUI_FaceAnalysis
pip install -r requirements.txt
```

### **Step 2: Download Required Models**

The extension needs these models (they download automatically on first use):

**Face Detection Models:**
- `retinaface_resnet50` (recommended)
- `retinaface_mobile0.25`

**Face Landmark Models:**
- `2dfan4` (recommended)
- `1k3d68`

**Face Parsing Models:**
- `79999_iter` (recommended)
- `face_parsing_512`

### **Step 3: Verify Installation**

1. **Restart ComfyUI completely**
2. **Check for new nodes:**
   - `FaceAnalysis`
   - `FacePartsToMask`
   - `FaceBoundingBox`
   - `FaceLandmarks`

## 🧪 Test the Installation

Run our test script:
```bash
python test_eyes_faceanalysis.py
```

**Requirements for testing:**
1. ✅ ComfyUI running on `http://127.0.0.1:8188`
2. ✅ ComfyUI_FaceAnalysis extension installed
3. ✅ `real-dream-15.safetensors` model
4. ✅ `chad_sd1.5.safetensors` LoRA
5. ✅ `test_image.png` in project root

## 📊 How It Works

### **1. FaceAnalysis Node**
```json
{
  "image": "input_image",
  "face_analysis_model": "retinaface_resnet50",
  "face_landmark_model": "2dfan4", 
  "face_parsing_model": "79999_iter"
}
```

**This node analyzes the face and identifies all facial features.**

### **2. FacePartsToMask Node**
```json
{
  "face_analysis": "from_step_1",
  "face_parts": ["left_eye", "right_eye", "left_eyebrow", "right_eyebrow"],
  "expand_pixels": 10,
  "blur_radius": 5
}
```

**This creates a precise mask for ONLY the selected features.**

### **3. Available Face Parts**
- `left_eye`, `right_eye`
- `left_eyebrow`, `right_eyebrow`
- `nose`
- `upper_lip`, `lower_lip`
- `left_ear`, `right_ear`
- `face` (entire face)
- `neck`
- `cloth`
- `hair`
- `hat`
- `earring`
- `necklace`
- `glasses`

## 🎯 Our Test Workflow

**Eyes + Eyebrows Targeting:**
1. **Load** real-dream-15.safetensors + chad LoRA
2. **Analyze** face with FaceAnalysis
3. **Create mask** for eyes + eyebrows only
4. **Inpaint** only the masked areas
5. **Composite** result back to original

**Key advantages:**
- ✅ **Precise targeting** - only affects selected features
- ✅ **Clean edges** - proper masking and blending
- ✅ **Preserves** rest of the face unchanged
- ✅ **Professional results** - no artifacts

## 🚀 Next Steps After Testing

If the eyes test works:

1. **Create workflows for other features:**
   - `workflow_lips_faceanalysis.json`
   - `workflow_nose_faceanalysis.json`
   - `workflow_jaw_faceanalysis.json`

2. **Update the web app** to use feature-specific workflows

3. **Re-enable the feature selection UI**

4. **Deploy to Railway** with true feature targeting

## 🔍 Troubleshooting

**Extension not found:**
- Make sure you restarted ComfyUI after installation
- Check `ComfyUI/custom_nodes/ComfyUI_FaceAnalysis` exists

**Models not downloading:**
- Check internet connection
- Models download to `ComfyUI/models/face_analysis/`

**Workflow errors:**
- Verify all required models are available
- Check ComfyUI console for error messages

**No face detected:**
- Use clear, well-lit face images
- Face should be facing forward
- Try different face detection models

## 💡 Why This is Perfect

**Before (FaceDetailer):**
- ❌ Processes entire face
- ❌ Cannot target specific features
- ❌ Feature selection was cosmetic only

**After (FaceAnalysis):**
- ✅ **TRUE feature targeting**
- ✅ **Precise masks** for any facial area
- ✅ **Professional results**
- ✅ **User gets exactly what they select**

This is the breakthrough we needed for **real feature-specific face morphing**!
