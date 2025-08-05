"""
Configuration file for Face Morphing Web App
Modify these settings to customize your application
"""

import os

# Flask Configuration
SECRET_KEY = 'your-secret-key-change-in-production'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
DEBUG = True

# Directory Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
WORKFLOW_FOLDER = 'comfyui_workflows'

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
        0.15: '+2 Tier',
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
        'denoise': 0.15,
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

# Development vs Production
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///face_morph.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

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
    '100': {'credits': 100, 'price': 5.00, 'bonus': 0},
    '500': {'credits': 500, 'price': 20.00, 'bonus': 100},  # 20% bonus
    '1000': {'credits': 1000, 'price': 35.00, 'bonus': 300}  # 30% bonus
}

# Rate Limiting
FREE_GENERATIONS_PER_DAY = 1
MAX_GENERATIONS_PER_HOUR = 10  # For paid users
MAX_GENERATIONS_PER_DAY = 100  # For paid users

# Cloud GPU Configuration (RunPod)
# For serverless endpoints
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY', '')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', '')

# For RunPod pods (direct connection)
RUNPOD_POD_URL = os.getenv('RUNPOD_POD_URL', '')  # e.g., "149.36.1.79"
RUNPOD_POD_PORT = int(os.getenv('RUNPOD_POD_PORT', '8188'))  # ComfyUI port
USE_RUNPOD_POD = os.getenv('USE_RUNPOD_POD', 'false').lower() == 'true'

# Cloud GPU mode selection
USE_CLOUD_GPU = os.getenv('USE_CLOUD_GPU', 'false').lower() == 'true'  # Use direct ComfyUI connection by default

# RunPod Settings
RUNPOD_TIMEOUT = 300  # 5 minutes timeout for generation
RUNPOD_CHECK_INTERVAL = 5  # Check status every 5 seconds

if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    LOG_LEVEL = 'WARNING'
    LOGIN_DISABLED = False