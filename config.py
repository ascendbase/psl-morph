"""
Configuration file for Face Morphing Web App
Modify these settings to customize your application
"""

import os

# Development vs Production
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Flask Configuration
SECRET_KEY = 'your-secret-key-change-in-production'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
DEBUG = True

# Directory Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
WORKFLOW_FOLDER = 'comfyui_workflows'

# Facial Evaluation Folder - Use Railway volume path in production
# Check multiple Railway indicators for better detection
is_railway = any([
    os.getenv('RAILWAY_ENVIRONMENT'),
    os.getenv('RAILWAY_PROJECT_ID'),
    os.getenv('RAILWAY_SERVICE_ID'),
    os.getenv('DATABASE_URL', '').startswith('postgresql://'),
    os.path.exists('/app')  # Railway typically uses /app as working directory
])

if is_railway and ENVIRONMENT == 'production':
    FACIAL_EVALUATION_FOLDER = '/app/facial_evaluations'  # Railway volume mount path
elif is_railway:
    # We're on Railway but not in production mode - still use volume path
    FACIAL_EVALUATION_FOLDER = '/app/facial_evaluations'  # Railway volume mount path
else:
    FACIAL_EVALUATION_FOLDER = 'facial_evaluations'  # Local development path

# ComfyUI Configuration
COMFYUI_URL = os.getenv('COMFYUI_URL', 'http://127.0.0.1:8188')
COMFYUI_TIMEOUT = int(os.getenv('COMFYUI_TIMEOUT', '300'))  # 5 minutes timeout for requests

# File Upload Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_IMAGE_SIZE = (2048, 2048)  # Maximum image dimensions
MIN_IMAGE_SIZE = (256, 256)    # Minimum image dimensions

# Transformation Tier System (10% to 25% denoise range)
TIER_SYSTEM = {
    'min_denoise': 0.10,  # 10% minimum
    'max_denoise': 0.25,  # 25% maximum
    'milestones': {
        0.10: '+1 Tier',
        0.17: '+2 Tier',
        0.25: 'Chad'
    }
}

# Legacy presets for backward compatibility (will be replaced by slider)
PRESETS = {
    'tier1': {
        'denoise': 0.10,
        'name': '+1 Tier',
        'description': 'Subtle Enhancement',
        'color': 'green'
    },
    'tier2': {
        'denoise': 0.17,
        'name': '+2 Tier',
        'description': 'Moderate Transform',
        'color': 'blue'
    },
    'chad': {
        'denoise': 0.25,
        'name': 'Chad',
        'description': 'Maximum Power',
        'color': 'orange'
    }
}

# Workflow Configuration
DEFAULT_WORKFLOW_FILE = 'workflow_fixed.json'  # ReActor face swap (current)

# Available workflow options
WORKFLOW_OPTIONS = {
    'reactor': {
        'file': 'workflow_fixed.json',
        'name': 'ReActor Face Swap',
        'description': 'Uses ReActor extension for face swapping'
    },
    'facedetailer': {
        'file': 'workflow_facedetailer.json',
        'name': 'FaceDetailer Inpainting',
        'description': 'Uses FaceDetailer for precise face detection and inpainting (recommended)'
    },
    'inpaint': {
        'file': 'workflow_inpaint_face.json',
        'name': 'Face Inpainting',
        'description': 'Uses SAM for face detection and inpainting'
    },
    'composite': {
        'file': 'workflow_face_mask.json',
        'name': 'Face Detection + Composite',
        'description': 'Uses FaceDetailer for detection and compositing'
    },
    'advanced': {
        'file': 'workflow_mask_composite.json',
        'name': 'Advanced Masking',
        'description': 'Uses UltralyticsDetector with advanced masking'
    }
}

# Current workflow mode
CURRENT_WORKFLOW = 'facedetailer'  # Testing fixed FaceDetailer workflow
WORKFLOW_PARAMETERS = {
    'steps': 20,
    'cfg': 8,
    'sampler_name': 'dpmpp_2m',
    'scheduler': 'normal',
    'lora_strength_model': 0.8,
    'lora_strength_clip': 0.85
}

# Security Configuration
SECURE_FILENAME_ENABLED = True
VALIDATE_IMAGE_CONTENT = True
CLEANUP_TEMP_FILES = True
TEMP_FILE_LIFETIME = 3600  # 1 hour in seconds

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Server Configuration
HOST = '0.0.0.0'  # Change to '127.0.0.1' for localhost only
PORT = 5000
THREADED = True

# Database Configuration
# Check if we're on Railway (Railway sets DATABASE_URL automatically)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # We're on Railway or another cloud platform with PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
        # Fix for newer SQLAlchemy versions
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Local development - use SQLite
    DATABASE_URL = 'sqlite:///instance/app.db'

# Authentication Configuration
LOGIN_DISABLED = os.getenv('LOGIN_DISABLED', 'False').lower() == 'true'  # For development
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# Payment Configuration
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')

# Credit System Configuration
CREDIT_PACKAGES = {
    '20': {'credits': 20, 'price': 10.00, 'bonus': 0},
    '50': {'credits': 50, 'price': 20.00, 'bonus': 5},  # 10% bonus
    '100': {'credits': 100, 'price': 36.00, 'bonus': 15},  # 15% bonus
    '250': {'credits': 250, 'price': 80.00, 'bonus': 50}  # 20% bonus
}

# Rate Limiting
FREE_GENERATIONS_PER_DAY = 1
MAX_GENERATIONS_PER_HOUR = 10  # For paid users
MAX_GENERATIONS_PER_DAY = 100  # For paid users

# Cloud GPU Configuration (RunPod)
# For serverless endpoints (recommended for cost efficiency - 95-99% cost savings!)
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY', '')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', '')
RUNPOD_SERVERLESS_ENDPOINT = os.getenv('RUNPOD_SERVERLESS_ENDPOINT', '')
RUNPOD_SERVERLESS_URL = os.getenv('RUNPOD_SERVERLESS_URL', '')

# Vast.ai Configuration (Pay-Per-Use - 98-99% cost savings!)
VAST_API_KEY = os.getenv('VAST_API_KEY', 'eaa3a310030819c8de5e1826678266244a6f761efacbc948aca66ca880f071db')
VAST_ON_DEMAND_MODE = os.getenv('VAST_ON_DEMAND_MODE', 'true').lower() == 'true'
VAST_AUTO_STOP_INSTANCES = os.getenv('VAST_AUTO_STOP_INSTANCES', 'true').lower() == 'true'
VAST_MAX_INSTANCE_LIFETIME = int(os.getenv('VAST_MAX_INSTANCE_LIFETIME', '300'))  # 5 minutes max
VAST_MIN_GPU_RAM = int(os.getenv('VAST_MIN_GPU_RAM', '8'))  # Minimum 8GB GPU RAM
VAST_MAX_HOURLY_COST = float(os.getenv('VAST_MAX_HOURLY_COST', '1.0'))  # Max $1/hour

# For RunPod pods (direct connection) - DEPRECATED, use serverless instead
RUNPOD_POD_URL = os.getenv('RUNPOD_POD_URL', 'https://i01ikv3a648vzu-8188.proxy.runpod.net')  # Your RTX 5090 GPU
RUNPOD_POD_PORT = int(os.getenv('RUNPOD_POD_PORT', '8188'))  # ComfyUI port
USE_RUNPOD_POD = os.getenv('USE_RUNPOD_POD', 'false').lower() == 'true'  # Disable pod by default - USE SERVERLESS!

# Modal.com Configuration (Perfect balance: Fast + Custom Models + Cheap)
USE_MODAL = os.getenv('USE_MODAL', 'false').lower() == 'true'  # DISABLED - Using local ComfyUI
MODAL_TOKEN = os.getenv('MODAL_TOKEN', '')
MODAL_APP_NAME = os.getenv('MODAL_APP_NAME', 'face-morph-simple')

# Replicate Configuration (Fallback option)
USE_REPLICATE = os.getenv('USE_REPLICATE', 'false').lower() == 'true'
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

# OpenRouter Configuration (for AI facial analysis)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')

# Cloud GPU mode selection - DISABLED FOR LOCAL COMFYUI
USE_CLOUD_GPU = os.getenv('USE_CLOUD_GPU', 'false').lower() == 'true'

# Local ComfyUI Configuration (for Railway deployment calling local GPU)
USE_LOCAL_COMFYUI = os.getenv('USE_LOCAL_COMFYUI', 'true').lower() == 'true'  # ENABLED - Use local ComfyUI
LOCAL_COMFYUI_URL = os.getenv('LOCAL_COMFYUI_URL', 'https://statute-pas-org-southeast.trycloudflare.com')  # Cloudflare tunnel URL
LOCAL_COMFYUI_WORKFLOW = os.getenv('LOCAL_COMFYUI_WORKFLOW', 'comfyui_workflows/workflow_facedetailer.json')

# RunPod Settings
RUNPOD_TIMEOUT = 300  # 5 minutes timeout for generation
RUNPOD_CHECK_INTERVAL = 5  # Check status every 5 seconds

if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    LOG_LEVEL = 'WARNING'
    LOGIN_DISABLED = False
