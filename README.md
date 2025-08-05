# 🔥 Face Morphing Web App

Transform faces with AI-powered morphing using your custom LoRA models with cloud GPU processing or local ComfyUI workflow.

## ✨ Features

- **Simple Web Interface**: Drag & drop image upload with user authentication
- **Three Transformation Levels**:
  - 🟢 **HTN** (30% denoise) - Minimal Enhancement
  - 🔵 **Chadlite** (35% denoise) - Strong Transform
  - 🟠 **Chad** (40% denoise) - Extreme Power
- **Cloud GPU Processing**: RunPod Stable Diffusion XL serverless integration
- **Local Processing**: ComfyUI with FaceDetailer for precise face detection
- **User System**: Authentication, credits, and payment processing
- **Credit System**: Free tier (1 generation/day) + paid tier (100 credits/$5)
- **Payment Options**: Crypto and bank transfers (Kyrgyzstan-compatible)
- **Automated Workflow**: No manual Photoshop work needed
- **Real-time Progress**: Live status updates during processing
- **Easy Download**: One-click result download

## 🚀 Quick Start

### Choose Your Setup

**Option A: Cloud GPU (RunPod) - Recommended** ☁️
- No local GPU required
- Faster processing with professional GPUs
- Pay-per-use pricing
- See [RunPod Setup](#-runpod-cloud-gpu-setup) below

**Option B: Local ComfyUI** 💻
- Use your own GPU
- Full control over models and workflows
- One-time setup cost
- See [Local Setup](#-local-comfyui-setup) below

### Prerequisites

1. **Python 3.8+**: Required for the web app
2. **Database**: PostgreSQL (recommended) or SQLite for development
3. **Either**:
   - **RunPod Account**: For cloud GPU processing
   - **ComfyUI + GPU**: For local processing

> 📋 **New**: The app now supports both cloud GPU (RunPod) and local ComfyUI processing!

## ☁️ RunPod Cloud GPU Setup

### Step 1: Create RunPod Endpoint

1. **Sign up at [RunPod.io](https://runpod.io)** and add credits
2. **Create a new Serverless Endpoint**:
   - Template: "Stable Diffusion XL"
   - GPU: RTX 4090 or A100
   - Name: `face-morphing-sdxl`
3. **Upload your LoRA** to a public URL (Hugging Face, Google Drive, etc.)
4. **Copy your API key and Endpoint ID**

### Step 2: Configure Environment

```bash
# Copy the RunPod example configuration
cp .env.runpod.example .env

# Edit .env with your RunPod details:
USE_CLOUD_GPU=true
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_LORA_URL=https://your-lora-url.com/chad_sd1.5.safetensors
```

### Step 3: Install Dependencies & Run

```bash
# Install Python dependencies
pip install -r requirements.txt

# Test RunPod connection
python test_runpod.py

# Run the app
python app.py
```

📖 **Detailed Guide**: See [`RUNPOD_SETUP.md`](RUNPOD_SETUP.md) for complete setup instructions.

---

## 💻 Local ComfyUI Setup

### Step 1: Setup ComfyUI API Server

1. Navigate to your ComfyUI directory
2. Start ComfyUI with API enabled:
   ```bash
   python main.py --listen 127.0.0.1 --port 8188
   ```
   
   Or if you want network access:
   ```bash
   python main.py --listen 0.0.0.0 --port 8188
   ```

3. Verify ComfyUI is running by visiting: http://127.0.0.1:8188

### Step 2: Install Web App Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Configure Your Models

1. **Copy your models to ComfyUI directories**:
   ```
   ComfyUI/models/checkpoints/real-dream-15.safetensors
   ComfyUI/models/loras/chad_sd1.5.safetensors
   ```

2. **Or update the workflow.json** to point to your model locations

### Step 4: Configure Environment

```bash
# Create environment file
cp .env.example .env

# Edit .env:
USE_CLOUD_GPU=false
COMFYUI_URL=http://127.0.0.1:8188
```

### Step 5: Run the Web App

```bash
python app.py
```

The app will start on: http://localhost:5000

## 📁 Project Structure

```
Morph-app/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models (User, Generation, etc.)
├── auth.py                   # Authentication routes
├── payments.py               # Payment processing
├── runpod_client.py          # RunPod API client
├── comfyui_client.py         # ComfyUI API client
├── requirements.txt          # Python dependencies
├── .env.runpod.example       # RunPod configuration example
├── test_runpod.py            # RunPod integration test
├── templates/
│   ├── landing.html          # Landing page
│   ├── index.html            # Main app interface
│   ├── dashboard.html        # User dashboard
│   ├── login.html            # Login page
│   └── register.html         # Registration page
├── comfyui_workflows/
│   └── workflow_*.json       # ComfyUI workflows
├── uploads/                  # Temporary uploaded images
├── outputs/                  # Generated results
├── deployment/               # Deployment configurations
├── RUNPOD_SETUP.md          # RunPod setup guide
└── FACEDETAILER_SETUP.md    # FaceDetailer setup guide
```

## 🔄 Workflow Options

The app supports multiple AI processing workflows:

### FaceDetailer (Recommended) 🌟
- **Superior Quality**: Advanced face detection with YOLO + SAM
- **Natural Results**: Better integration with surrounding areas
- **Precise Masking**: Pixel-perfect face boundaries
- **Setup**: See [`FACEDETAILER_SETUP.md`](FACEDETAILER_SETUP.md) for installation

### ReActor (Fallback) ⚡
- **Fast Processing**: Quick face swapping
- **Simple Setup**: Minimal dependencies
- **Reliable**: Proven workflow for basic transformations
- **Default**: Works out of the box

### Switching Workflows
Edit [`config.py`](config.py:82) to change the active workflow:
```python
CURRENT_WORKFLOW = 'facedetailer'  # or 'reactor'
```

## ⚙️ Configuration

### ComfyUI Connection

Edit [`app.py`](app.py:25) to change ComfyUI URL:
```python
COMFYUI_URL = 'http://127.0.0.1:8188'  # Change if needed
```

### Preset Settings

The three transformation levels are defined in [`app.py`](app.py:30):
```python
PRESETS = {
    'HTN': {'denoise': 0.30, 'name': 'HTN', 'description': 'Subtle Enhancement'},
    'Chadlite': {'denoise': 0.35, 'name': 'Chadlite', 'description': 'Moderate Transform'},
    'Chad': {'denoise': 0.40, 'name': 'Chad', 'description': 'Maximum Power'}
}
```

### File Upload Limits

Modify in [`app.py`](app.py:18):
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

## 🔧 Troubleshooting

### ComfyUI Connection Issues

1. **Check if ComfyUI is running**: Visit http://127.0.0.1:8188
2. **Verify API is enabled**: ComfyUI should show "API server running"
3. **Check firewall**: Make sure port 8188 is not blocked

### Model Loading Issues

1. **Verify model paths** in your [`workflow.json`](comfyui_workflows/workflow.json)
2. **Check model files exist** in ComfyUI directories
3. **Ensure LoRA file** [`chad_sd1.5.safetensors`](lora/chad_sd1.5.safetensors) is accessible

### Upload Issues

1. **Check file format**: Only PNG, JPG, JPEG, WebP supported
2. **File size limit**: Maximum 16MB per image
3. **Image dimensions**: Maximum 2048x2048 pixels

## 🌐 Deployment Options

### Local Network Access

Change the Flask host in [`app.py`](app.py:295):
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Cloud Deployment

The app is ready for cloud deployment on:
- **Railway**: Add `railway.toml` configuration
- **Render**: Works with current `requirements.txt`
- **AWS/GCP**: Use Docker or direct deployment
- **Heroku**: Add `Procfile` for web process

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🔒 Security Notes

- File uploads are validated for type and size
- Temporary files are cleaned up automatically
- No user data is permanently stored
- Consider adding authentication for production use

## 🎯 Usage Tips

1. **Best Results**: Use clear, well-lit face photos
2. **Image Quality**: Higher resolution input = better output
3. **Face Position**: Centered faces work best
4. **Lighting**: Even lighting produces more consistent results

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Landing page or dashboard (if authenticated)
- `GET /health` - Health check and GPU status
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Authenticated Endpoints
- `GET /dashboard` - User dashboard with stats and credits
- `GET /app` - Main app interface
- `POST /upload` - Upload image file
- `POST /process` - Start processing workflow (RunPod or ComfyUI)
- `GET /status/<prompt_id>` - Check processing status
- `GET /result/<prompt_id>` - Download result
- `GET /auth/profile` - User profile page

### Payment Endpoints
- `POST /payments/crypto` - Process crypto payment
- `POST /payments/bank` - Process bank transfer
- `GET /payments/status/<transaction_id>` - Check payment status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your ComfyUI setup is working
3. Check the browser console for JavaScript errors
4. Review the Flask logs for server errors

---

**Made with ❤️ for the AI community**