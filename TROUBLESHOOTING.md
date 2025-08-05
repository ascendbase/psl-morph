# 🔧 Troubleshooting Guide

## 🐍 Python Dependency Issues

### Problem: Pillow Installation Fails
**Error**: `Getting requirements to build wheel did not run successfully`

**Solutions**:

#### Option 1: Use Flexible Requirements
```bash
pip install -r requirements-flexible.txt
```

#### Option 2: Install Individual Packages
```bash
pip install Flask Pillow requests Werkzeug
```

#### Option 3: Use Pre-compiled Wheels
```bash
pip install --only-binary=all Flask Pillow requests Werkzeug
```

#### Option 4: For Python 3.13+
```bash
pip install --upgrade pip
pip install Flask>=3.0.0 Pillow>=10.4.0 requests>=2.32.0 Werkzeug>=3.0.0
```

### Problem: Python Version Compatibility
**Error**: Package versions not compatible with your Python version

**Solutions**:
1. **Check Python Version**: `python --version`
2. **Use Compatible Versions**:
   - Python 3.8-3.11: Use `requirements.txt`
   - Python 3.12+: Use `requirements-flexible.txt`
3. **Consider Downgrading Python** to 3.11 if issues persist

## 🔗 ComfyUI Connection Issues

### Problem: Cannot Connect to ComfyUI
**Error**: `Cannot connect to ComfyUI. Make sure ComfyUI is running with API enabled.`

**Solutions**:

#### 1. Start ComfyUI with API
```bash
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

#### 2. Check if ComfyUI is Running
- Open browser: http://127.0.0.1:8188
- Should show ComfyUI interface

#### 3. Verify API Endpoint
```bash
curl http://127.0.0.1:8188/system_stats
```

#### 4. Check Firewall
- Windows: Allow Python through Windows Firewall
- Antivirus: Add ComfyUI folder to exclusions

### Problem: ComfyUI Starts but API Doesn't Work
**Solutions**:
1. **Restart ComfyUI** with explicit API flag:
   ```bash
   python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header
   ```

2. **Check ComfyUI Console** for error messages

3. **Update ComfyUI** to latest version

## 📁 File and Model Issues

### Problem: Models Not Found
**Error**: Workflow fails with missing model errors

**Solutions**:

#### 1. Check Model Locations
```
ComfyUI/models/checkpoints/real-dream-15.safetensors
ComfyUI/models/loras/chad_sd1.5.safetensors
ComfyUI/models/insightface/inswapper_128.onnx
```

#### 2. Update Workflow Paths
Edit `comfyui_workflows/workflow.json` to match your model paths

#### 3. Copy Models to Correct Locations
```bash
# Copy your models to ComfyUI directories
cp base_models/* ComfyUI/models/checkpoints/
cp lora/* ComfyUI/models/loras/
```

### Problem: ReActor Extension Missing
**Error**: ReActorFaceSwap node not found

**Solutions**:
1. **Install ReActor Extension**:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Gourieff/comfyui-reactor-node.git
   cd comfyui-reactor-node
   pip install -r requirements.txt
   ```

2. **Download ReActor Model**:
   - Download `inswapper_128.onnx`
   - Place in `ComfyUI/models/insightface/`

3. **Restart ComfyUI** after installing extensions

### Problem: Impact Pack Extension Conflicts
**Error**: `argument of type 'int' is not iterable` or `Cannot execute because a node is missing the class_type property`

**Solutions**:
1. **Use Fixed Workflow**: The app now uses `workflow_fixed.json` which avoids Impact Pack conflicts
2. **Disable Impact Pack** temporarily:
   ```bash
   # Rename the extension folder to disable it
   cd ComfyUI/custom_nodes
   mv comfyui-inspire-pack comfyui-inspire-pack.disabled
   ```
3. **Update Impact Pack**:
   ```bash
   cd ComfyUI/custom_nodes/comfyui-inspire-pack
   git pull
   ```
4. **Clean Workflow**: The fixed workflow uses standard ComfyUI nodes only

### Problem: Invalid Workflow JSON
**Error**: `invalid prompt` or JSON parsing errors

**Solutions**:
1. **Use Fixed Workflow**: App automatically uses the clean `workflow_fixed.json`
2. **Validate JSON**: Check if your workflow JSON is properly formatted
3. **Export New Workflow**: Create a fresh workflow in ComfyUI and export it
4. **Check Node IDs**: Ensure all nodes have proper `class_type` properties

## 🌐 Web App Issues

### Problem: Web App Won't Start
**Error**: Various Flask/server errors

**Solutions**:

#### 1. Check Port Availability
```bash
# Windows
netstat -an | findstr :5000

# Linux/Mac
lsof -i :5000
```

#### 2. Try Different Port
Edit `config.py`:
```python
PORT = 5001  # Change from 5000
```

#### 3. Run with Debug Info
```bash
python app.py
```
Check console output for specific errors

### Problem: File Upload Fails
**Error**: Upload errors or validation failures

**Solutions**:
1. **Check File Size**: Max 16MB by default
2. **Check File Format**: Only PNG, JPG, JPEG, WebP
3. **Check Permissions**: Ensure write access to `uploads/` folder

### Problem: Processing Stuck
**Error**: Processing never completes

**Solutions**:
1. **Check ComfyUI Console** for errors
2. **Restart ComfyUI** if it's frozen
3. **Check GPU Memory** - may be out of VRAM
4. **Try Smaller Image** or lower resolution

## 🖥️ System-Specific Issues

### Windows Issues

#### Problem: Script Execution Policy
**Error**: Cannot run PowerShell scripts

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Problem: Long Path Names
**Error**: Path too long errors

**Solution**:
1. Move project to shorter path (e.g., `C:\Morph\`)
2. Enable long paths in Windows

### Linux/Mac Issues

#### Problem: Permission Denied
**Error**: Cannot execute startup script

**Solution**:
```bash
chmod +x start.sh
```

#### Problem: Python Command Not Found
**Error**: `python: command not found`

**Solution**:
```bash
# Use python3 instead
python3 app.py

# Or create alias
alias python=python3
```

## 🔍 Debugging Steps

### 1. Check System Health
```bash
# Test web app health
curl http://localhost:5000/health

# Test ComfyUI health
curl http://127.0.0.1:8188/system_stats
```

### 2. Enable Debug Mode
Edit `config.py`:
```python
DEBUG = True
LOG_LEVEL = 'DEBUG'
```

### 3. Check Logs
- Web app logs: Console output when running `python app.py`
- ComfyUI logs: ComfyUI console window
- Browser logs: F12 → Console tab

### 4. Test Components Individually
1. **Test ComfyUI**: Load workflow manually in ComfyUI interface
2. **Test Upload**: Try uploading different image formats/sizes
3. **Test API**: Use curl to test endpoints directly

## 📞 Getting Help

### Before Asking for Help
1. ✅ Check this troubleshooting guide
2. ✅ Read error messages carefully
3. ✅ Test with different images/settings
4. ✅ Check all components are running

### Information to Include
- **Python Version**: `python --version`
- **Operating System**: Windows/Linux/Mac version
- **Error Messages**: Full error text
- **Steps to Reproduce**: What you did before the error
- **ComfyUI Status**: Is it running? Any errors?

### Quick Fixes to Try
1. **Restart Everything**: ComfyUI, web app, browser
2. **Clear Browser Cache**: Hard refresh (Ctrl+F5)
3. **Try Different Image**: Smaller size, different format
4. **Check Disk Space**: Ensure enough free space
5. **Update Dependencies**: `pip install --upgrade -r requirements.txt`

---

**Most issues are resolved by ensuring ComfyUI is running properly with API enabled and all dependencies are correctly installed.**