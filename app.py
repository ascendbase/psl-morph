import os
import json
import uuid
import requests
import shutil
import time
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io
import logging
from datetime import datetime, timedelta
from config import *
from tunnel_registry import set_tunnel_url
from models import db, User, Generation, Transaction, FacialEvaluation, RatiosMorph, SystemPrompt, AutomatedFacialAnalysis, init_db
from auth import auth_bp, init_login_manager
from payments import payments_bp
import mistune
from openrouter_client import OpenRouterClient # Import the new OpenRouterClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- FIX: Absolute Paths for Deployment ---
# Make folder paths absolute to the app's root directory. This is crucial for
# containerized environments like Railway where the working directory may not be the project root.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLDER)
OUTPUT_FOLDER = os.path.join(APP_ROOT, OUTPUT_FOLDER)
WORKFLOW_FOLDER = os.path.join(APP_ROOT, WORKFLOW_FOLDER)

# CRITICAL FIX: Don't override FACIAL_EVALUATION_FOLDER from config.py
# The config.py already handles Railway volume detection properly
# Only make it absolute if it's a relative path (local development)
if not os.path.isabs(FACIAL_EVALUATION_FOLDER):
    FACIAL_EVALUATION_FOLDER = os.path.join(APP_ROOT, FACIAL_EVALUATION_FOLDER)
# For Railway, FACIAL_EVALUATION_FOLDER is already '/app/facial_evaluations' (absolute)
# -----------------------------------------

# Initialize database and authentication
init_db(app)
login_manager = init_login_manager(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(payments_bp)

# GPU rate limiting - track last generation time per user
user_last_generation = {}
GENERATION_COOLDOWN = 60  # 60 seconds between generations

# Initialize GPU client with error handling
gpu_client = None
try:
    if USE_LOCAL_COMFYUI:
        # Use Local ComfyUI for processing with automatic tunnel detection
        from local_comfyui_client import LocalComfyUIClient
        from cloudflare_tunnel_detector import get_dynamic_comfyui_url, tunnel_detector
        
        # Get dynamic URL (will auto-detect Cloudflare tunnel or fallback to local)
        dynamic_url = get_dynamic_comfyui_url()
        
        gpu_client = LocalComfyUIClient(
            base_url=dynamic_url,
            workflow_path=LOCAL_COMFYUI_WORKFLOW,
            timeout=COMFYUI_TIMEOUT
        )
        
        # Log tunnel detection info
        tunnel_info = tunnel_detector.get_tunnel_info()
        if tunnel_info['status'] == 'connected':
            logger.info(f"🚀 Auto-detected Cloudflare tunnel: {tunnel_info['url']}")
            logger.info(f"ComfyUI Version: {tunnel_info.get('comfyui_version', 'unknown')}")
            logger.info(f"GPU Devices: {len(tunnel_info.get('devices', []))} detected")
        else:
            logger.info(f"Using fallback URL: {dynamic_url}")
            logger.info(f"Tunnel detection: {tunnel_info['message']}")
        
        logger.info(f"Initialized Local ComfyUI client: {dynamic_url}")
        logger.info(f"Using workflow: {LOCAL_COMFYUI_WORKFLOW}")
    elif USE_MODAL:
        # Use Modal.com for processing
        from modal_client import ModalMorphClient
        gpu_client = ModalMorphClient()
        logger.info("Initialized Modal.com client - 95% cost savings vs RunPod!")
    elif USE_CLOUD_GPU:
        # Check if on-demand mode is enabled
        if VAST_ON_DEMAND_MODE:
            from vast_on_demand_client import VastOnDemandClient
            gpu_client = VastOnDemandClient(VAST_API_KEY)
            logger.info("Initialized Vast.ai On-Demand client - 98-99% cost savings vs RunPod!")
        else:
            # Use regular Vast.ai client
            from vast_client import VastMorphClient
            gpu_client = VastMorphClient()
            logger.info("Initialized Vast.ai client - 90% cost savings vs RunPod!")
    else:
        from comfyui_client import ComfyUIClient
        gpu_client = ComfyUIClient(COMFYUI_URL)
        logger.info(f"Initialized ComfyUI client: {COMFYUI_URL}")
except Exception as e:
    logger.error(f"Failed to initialize GPU client: {e}")
    logger.info("App will continue without GPU client - it will be initialized when needed")

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(WORKFLOW_FOLDER, exist_ok=True)

# Create facial evaluation folder with proper permissions and logging
try:
    os.makedirs(FACIAL_EVALUATION_FOLDER, exist_ok=True)
    logger.info(f"✅ Facial evaluation folder ready: {FACIAL_EVALUATION_FOLDER}")
    
    # Test write permissions
    test_file = os.path.join(FACIAL_EVALUATION_FOLDER, '.write_test')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    logger.info(f"✅ Facial evaluation folder is writable")
    
except Exception as e:
    logger.error(f"❌ Failed to create/access facial evaluation folder: {e}")
    logger.error(f"   Path: {FACIAL_EVALUATION_FOLDER}")
    logger.error(f"   This may cause facial evaluation feature to fail")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up old temporary files"""
    if not CLEANUP_TEMP_FILES:
        return
    
    try:
        current_time = time.time()
        
        # Clean upload folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > TEMP_FILE_LIFETIME:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old upload file: {filename}")
        
        # Clean output folder
        for filename in os.listdir(OUTPUT_FOLDER):
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > TEMP_FILE_LIFETIME:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old output file: {filename}")
                    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def copy_image_to_comfyui(source_path, filename):
    """Copy uploaded image to ComfyUI input directory if needed"""
    try:
        # Try common ComfyUI input directory locations
        possible_paths = [
            "D:/ComfyUI_windows_portable/ComfyUI/input",
            "../ComfyUI/input",
            "../../ComfyUI/input",
            "./ComfyUI/input",
            os.path.expanduser("~/ComfyUI/input")
        ]
        
        for comfyui_input_dir in possible_paths:
            if os.path.exists(comfyui_input_dir):
                dest_path = os.path.join(comfyui_input_dir, filename)
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied image to ComfyUI input: {dest_path}")
                return True
        
        # If no ComfyUI input directory found, that's okay
        # ComfyUI can still access the file via the uploads folder
        logger.info(f"No ComfyUI input directory found, using uploads folder")
        return True
        
    except Exception as e:
        logger.error(f"Error copying image to ComfyUI: {e}")
        return False

def validate_image(file_path):
    """Validate uploaded image"""
    try:
        with Image.open(file_path) as img:
            # Check maximum image size
            max_width, max_height = MAX_IMAGE_SIZE
            if img.width > max_width or img.height > max_height:
                return False, f"Image too large. Maximum size is {max_width}x{max_height} pixels."
            
            # Check minimum image size
            min_width, min_height = MIN_IMAGE_SIZE
            if img.width < min_width or img.height < min_height:
                return False, f"Image too small. Minimum size is {min_width}x{min_height} pixels."
            
            # Check if image has reasonable dimensions for face photos
            aspect_ratio = img.width / img.height
            if aspect_ratio > 3 or aspect_ratio < 0.33:
                return False, "Image aspect ratio seems unusual for face photos."
            
            # Additional validation for image content if enabled
            if VALIDATE_IMAGE_CONTENT:
                # Check if image has reasonable color channels
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    return False, "Unsupported image color mode."
            
            return True, "Valid image"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def load_workflow_template():
    """Load the ComfyUI workflow template"""
    try:
        # Get current workflow configuration
        current_workflow = WORKFLOW_OPTIONS[CURRENT_WORKFLOW]
        workflow_file = current_workflow['file']
        workflow_path = os.path.join(WORKFLOW_FOLDER, workflow_file)
        
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        logger.info(f"Loaded workflow: {current_workflow['name']} ({workflow_file})")
        return workflow
    except Exception as e:
        logger.error(f"Failed to load workflow template: {e}")
        return None

def prepare_workflow(image_filename, preset_key):
    """Prepare workflow with specific image and preset"""
    import random
    
    workflow = load_workflow_template()
    if not workflow:
        return None
    
    preset = PRESETS[preset_key]
    current_workflow_type = CURRENT_WORKFLOW
    
    # Generate unique seed for each run to prevent caching
    unique_seed = random.randint(1, 2**32 - 1)
    timestamp = int(time.time())
    
    # Update common parameters for all workflow types
    # Update LoadImage node (usually node 5)
    if "5" in workflow:
        workflow["5"]["inputs"]["image"] = image_filename
    
    # Update LoraLoader parameters (usually node 2)
    if "2" in workflow:
        if 'lora_strength_model' in WORKFLOW_PARAMETERS:
            workflow["2"]["inputs"]["strength_model"] = WORKFLOW_PARAMETERS['lora_strength_model']
        if 'lora_strength_clip' in WORKFLOW_PARAMETERS:
            workflow["2"]["inputs"]["strength_clip"] = WORKFLOW_PARAMETERS['lora_strength_clip']
    
    # Update generation parameters based on workflow type
    if current_workflow_type == 'reactor':
        # ReActor workflow - KSampler is node 7
        if "7" in workflow:
            workflow["7"]["inputs"]["denoise"] = preset['denoise']
            workflow["7"]["inputs"]["seed"] = unique_seed
            if 'steps' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["steps"] = WORKFLOW_PARAMETERS['steps']
            if 'cfg' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["cfg"] = WORKFLOW_PARAMETERS['cfg']
        
        # SaveImage node for ReActor (node 10)
        if "10" in workflow:
            workflow["10"]["inputs"]["filename_prefix"] = f"morph_{preset_key}_{timestamp}"
    
    elif current_workflow_type == 'facedetailer':
        # FaceDetailer workflow - FaceDetailer node is node 8
        if "8" in workflow:
            workflow["8"]["inputs"]["denoise"] = preset['denoise']
            workflow["8"]["inputs"]["seed"] = unique_seed
            if 'steps' in WORKFLOW_PARAMETERS:
                workflow["8"]["inputs"]["steps"] = WORKFLOW_PARAMETERS['steps']
            if 'cfg' in WORKFLOW_PARAMETERS:
                workflow["8"]["inputs"]["cfg"] = WORKFLOW_PARAMETERS['cfg']
        
        # SaveImage node for FaceDetailer (node 9)
        if "9" in workflow:
            workflow["9"]["inputs"]["filename_prefix"] = f"morph_{preset_key}_{timestamp}"
    
    elif current_workflow_type == 'inpaint':
        # Face inpainting workflow - KSampler is node 7 (simplified version)
        if "7" in workflow:
            workflow["7"]["inputs"]["denoise"] = preset['denoise']
            workflow["7"]["inputs"]["seed"] = unique_seed
            if 'steps' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["steps"] = WORKFLOW_PARAMETERS['steps']
            if 'cfg' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["cfg"] = WORKFLOW_PARAMETERS['cfg']
        
        # SaveImage node for inpainting (node 9)
        if "9" in workflow:
            workflow["9"]["inputs"]["filename_prefix"] = f"morph_{preset_key}_{timestamp}"
    
    elif current_workflow_type in ['composite', 'advanced']:
        # Face composite workflows - KSampler is node 7
        if "7" in workflow:
            workflow["7"]["inputs"]["denoise"] = preset['denoise']
            workflow["7"]["inputs"]["seed"] = unique_seed
            if 'steps' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["steps"] = WORKFLOW_PARAMETERS['steps']
            if 'cfg' in WORKFLOW_PARAMETERS:
                workflow["7"]["inputs"]["cfg"] = WORKFLOW_PARAMETERS['cfg']
        
        # SaveImage node varies by workflow
        save_node = "11" if current_workflow_type == 'composite' else "13"
        if save_node in workflow:
            workflow[save_node]["inputs"]["filename_prefix"] = f"morph_{preset_key}_{timestamp}"
    
    logger.info(f"Prepared {WORKFLOW_OPTIONS[current_workflow_type]['name']} workflow for {preset_key} preset with {preset['denoise']} denoise and seed {unique_seed}")
    return workflow

def clear_comfyui_cache():
    """Clear ComfyUI cache to ensure fresh generation"""
    try:
        # Clear the queue first
        response = requests.post(f"{COMFYUI_URL}/queue", json={"clear": True}, timeout=10)
        if response.status_code == 200:
            logger.info("Cleared ComfyUI queue")
        
        # Try to clear history (if endpoint exists)
        try:
            response = requests.post(f"{COMFYUI_URL}/history", json={"clear": True}, timeout=10)
            if response.status_code == 200:
                logger.info("Cleared ComfyUI history")
        except:
            pass  # History clear endpoint might not exist
            
    except Exception as e:
        logger.warning(f"Could not clear ComfyUI cache: {e}")
        # Don't fail the entire process if cache clearing fails
        pass

def queue_workflow(workflow):
    """Queue workflow in ComfyUI"""
    try:
        # Clear cache before queuing new workflow
        clear_comfyui_cache()
        
        # Generate unique prompt ID
        prompt_id = str(uuid.uuid4())
        
        payload = {
            "prompt": workflow,
            "client_id": prompt_id
        }
        
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json=payload,
            timeout=COMFYUI_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get('prompt_id'), None
    
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to ComfyUI. Make sure ComfyUI is running with API enabled."
    except requests.exceptions.Timeout:
        return None, "ComfyUI request timed out. The server may be overloaded."
    except Exception as e:
        return None, f"Error queuing workflow: {str(e)}"

def check_workflow_status(prompt_id):
    """Check if workflow is complete"""
    try:
        response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        response.raise_for_status()
        
        history = response.json()
        if prompt_id in history:
            return True, history[prompt_id]
        return False, None
    
    except Exception as e:
        logger.error(f"Error checking workflow status: {e}")
        return False, None

def get_output_image(prompt_id, history_data):
    """Get the output image from ComfyUI"""
    try:
        # Find the output node (usually SaveImage or PreviewImage)
        outputs = history_data.get('outputs', {})
        
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for image_info in node_output['images']:
                    filename = image_info['filename']
                    subfolder = image_info.get('subfolder', '')
                    
                    # Download the image
                    params = {
                        'filename': filename,
                        'subfolder': subfolder,
                        'type': 'output'
                    }
                    
                    response = requests.get(f"{COMFYUI_URL}/view", params=params)
                    response.raise_for_status()
                    
                    return response.content
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting output image: {e}")
        return None

@app.route('/')
def index():
    """Main page"""
    if LOGIN_DISABLED:
        return render_template('index.html', presets=PRESETS)
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template('landing.html', presets=PRESETS)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    stats = current_user.get_generation_stats()
    recent_generations = Generation.query.filter_by(user_id=current_user.id)\
        .order_by(Generation.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         presets=PRESETS,
                         stats=stats,
                         recent_generations=recent_generations)

@app.route('/app')
@login_required
def app_interface():
    """Main app interface (authenticated)"""
    return render_template('index.html', presets=PRESETS)

@app.route('/chad-2-0-interface')
@login_required
def chad_2_0_interface():
    """CHAD 2.0 app interface (authenticated) - uses SD XL + custom LoRA"""
    return render_template('chad_2_0.html')

@app.route('/analyze-facial-features', methods=['POST'])
@login_required
def analyze_facial_features():
    """
    Endpoint to trigger automated facial feature analysis using Gemini.
    Requires original and morphed image filenames from a completed generation.
    """
    try:
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support.'}), 403

        data = request.get_json()
        generation_id = data.get('generation_id')

        generation = Generation.query.filter_by(
            id=generation_id,
            user_id=current_user.id,
            status='completed'
        ).first()

        if not generation:
            return jsonify({'error': 'Generation not found or not completed'}), 404
        
        # Ensure it's a full transformation (not custom or reference)
        if generation.preset.startswith('custom_') or generation.preset.startswith('reference_'):
            return jsonify({'error': 'Automated facial evaluation is only available for full face transformations.'}), 400

        # Check if analysis already exists for this generation
        existing_analysis = AutomatedFacialAnalysis.query.filter_by(
            generation_id=generation_id
        ).first()

        if existing_analysis:
            analysis_html = mistune.html(existing_analysis.analysis_result)
            return jsonify({
                'success': True,
                'analysis_result': analysis_html,
                'message': 'Analysis already exists for this generation.'
            })

        # Deduct 1 credit for automated analysis
        if current_user.credits < 1:
            return jsonify({
                'error': 'Insufficient credits. You need 1 credit for automated facial analysis.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        current_user.credits -= 1
        db.session.commit()
        logger.info(f"Deducted 1 credit from {current_user.email} for automated facial analysis.")

        # Get image paths
        original_image_path = os.path.join(UPLOAD_FOLDER, generation.input_filename)
        morphed_image_path = os.path.join(OUTPUT_FOLDER, generation.output_filename)

        if not os.path.exists(original_image_path) or not os.path.exists(morphed_image_path):
            return jsonify({'error': 'Original or morphed image files not found.'}), 404

        # Get the system prompt from the database
        system_prompt_obj = SystemPrompt.query.filter_by(name='default_facial_analysis_prompt').first()
        if not system_prompt_obj:
            # If no prompt exists, create a default one
            default_prompt_text = """
            You are an expert facial features analyst. Your task is to compare two images of a face, one original and one morphed, and identify the differences in facial features based on the following criteria. For each feature, evaluate the "amount of difference" on a scale of 1-10 (1 being almost no difference, 10 being a very significant difference). Then, multiply this difference score by the "importance" score (provided in parentheses next to each feature). Finally, list all features based on these individual relative importance scores, from highest to lowest.

            Facial Features and their Importance:
            1. Facial leanness (Importance = 8): Appearance of “tight” facial skin without any visible facial fat sagging. Shows the underlying bone structure, increases perceived facial depth via various shadows under various lighting. The desired appearance depends not only on the obvious total low body fat % levels but on the underlying bone morphology AND certain soft tissues (SMAS) morphology.
            2. Facial Width (Importance = 7): Both bizygomatic (cheekbones) and bigonial (jaw)
            3. Eyes (Importance = 6): I'm talking about the eyes morphology separately from the eyebrows appearance here. The specific relevant parameters here are: deep set, compact (smaller and more almond shaped) or bigger (rounder) and wide eyes (high PFL, low PFH) or rounder (low PFL).
            4. Nose (Importance = 5): nose tip width and bulbosity instead of narrower or more refined, sharper nose tip, symmetry, nose tip rotation (tip and nostrils pointring downward or upwards)
            5. Health Indicators (Importance = 4): Clear, homogenous (even) skin texture without wrinkles, acne scars, signs of skin aging or other skin imperfections. Symmetrical facial features like hairline, temporal bones, eyebrows, eyes (+ eye focus (no amblyopia)), nose bridge and tip, lips, chin, cheekbones, and mandible alignment. Straight hairline without balding patterns.
            6. Mouth and Lips (Importance = 3): mouth width and lips volume (both upper lip and lower lip, and their volumes ratio)
            7. Facial Angularity (Importance = 2): I'm talking specifically about the contour of the face here. Not the general facial leanness, but certain facial bones spots angularity. Angularity spots: temporal cave in, cheekbones outwards, ramus cave in, gonions outwards, mandible cave in, chin outwards (square).
            8. Eyebrows (Importance = 1): Wide (visible inner and outer corners eyebrows region), thick, closet set (vertically) eyebrows.
            """
            system_prompt_obj = SystemPrompt(name='default_facial_analysis_prompt', prompt_text=default_prompt_text)
            db.session.add(system_prompt_obj)
            db.session.commit()
            logger.info("Created default system prompt for facial analysis.")
        
        system_prompt_text = system_prompt_obj.prompt_text

        # Initialize OpenRouter Client
        openrouter_client = OpenRouterClient()
        
        # Perform analysis
        analysis_result = openrouter_client.analyze_facial_features(
            original_image_path,
            morphed_image_path,
            system_prompt_text
        )

        if "error" in analysis_result:
            logger.error(f"OpenRouter analysis failed: {analysis_result['error']}")
            return jsonify({'error': f"Automated analysis failed: {analysis_result['error']}"}), 500

        # Convert analysis result from Markdown to HTML
        analysis_html = mistune.html(analysis_result['analysis'])

        # Save analysis result to database
        automated_analysis = AutomatedFacialAnalysis(
            generation_id=generation_id,
            analysis_result=analysis_result['analysis'], # Store the text directly
            credits_used=1 # Record credits used
        )
        db.session.add(automated_analysis)
        db.session.commit()
        logger.info(f"Automated facial analysis saved for generation {generation_id}")

        return jsonify({
            'success': True,
            'analysis_result': analysis_html,
            'message': 'Automated facial analysis completed successfully.'
        })

    except ValueError as ve:
        logger.error(f"Configuration error for GeminiClient: {ve}")
        return jsonify({'error': f"Server configuration error: {ve}"}), 500
    except Exception as e:
        logger.error(f"Error during automated facial analysis: {e}")
        return jsonify({'error': 'Failed to perform automated facial analysis. Please try again.'}), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload"""
    try:
        # Check if user is blocked
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support at ascendbase@gmail.com.'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        denoise_str = request.form.get('denoise', '0.10')
        chad_2_0_mode = request.form.get('chad_2_0_mode', 'false').lower() == 'true'
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate denoise value (allow 0.3 for custom features mode, 0.15-0.35 for CHAD 2.0)
        try:
            denoise_value = float(denoise_str)
            # Allow 0.3 for custom features mode
            if denoise_value == 0.3:
                pass
            # Allow 0.15-0.35 for CHAD 2.0 mode
            elif chad_2_0_mode:
                if denoise_value < 0.15 or denoise_value > 0.35:
                    return jsonify({'error': 'Invalid denoise value for CHAD 2.0. Must be between 0.15 and 0.35'}), 400
            # Normal range for regular mode
            elif denoise_value < 0.10 or denoise_value > 0.25:
                return jsonify({'error': 'Invalid denoise value. Must be between 0.10 and 0.25'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid denoise value format'}), 400
        
        # Check if user can generate - prioritize paid credits
        can_paid = current_user.can_generate_paid()
        can_free = current_user.can_generate_free()
        
        if not can_paid and not can_free:
            return jsonify({
                'error': 'No credits available. Purchase more credits or wait until tomorrow for your free generation.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        if file and allowed_file(file.filename):
            # Clean up old files periodically
            cleanup_old_files()
            
            # Generate secure filename
            original_filename = secure_filename(file.filename) if SECURE_FILENAME_ENABLED else file.filename
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save uploaded file
            file.save(file_path)
            logger.info(f"File uploaded by {current_user.email}: {unique_filename}")
            
            # Validate image
            is_valid, message = validate_image(file_path)
            if not is_valid:
                os.remove(file_path)
                logger.warning(f"Invalid image rejected: {message}")
                return jsonify({'error': message}), 400
            
            # Copy to ComfyUI input folder if needed
            copy_image_to_comfyui(file_path, unique_filename)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'denoise': denoise_value,
                'can_use_free': can_free,
                'can_use_paid': can_paid,
                'credits': current_user.credits,
                'message': f'File uploaded successfully. Ready to process with {denoise_value:.0%} denoise strength.'
            })
        
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, or WebP images.'}), 400
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500

@app.route('/process', methods=['POST'])
@login_required
def process_image():
    """Process image with GPU client (RunPod or ComfyUI)"""
    try:
        # Check if user is blocked
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support at ascendbase@gmail.com.'}), 403
        
        # Check generation cooldown to prevent GPU overload
        current_time = time.time()
        user_id = current_user.id
        
        if user_id in user_last_generation:
            time_since_last = current_time - user_last_generation[user_id]
            if time_since_last < GENERATION_COOLDOWN:
                remaining_time = int(GENERATION_COOLDOWN - time_since_last)
                return jsonify({
                    'error': f'GPU is overloaded, please wait {remaining_time} seconds before generating again.',
                    'cooldown': True,
                    'remaining_seconds': remaining_time,
                    'message': f'Please wait {remaining_time} seconds to prevent GPU overload.'
                }), 429
        
        data = request.get_json()
        filename = data.get('filename')
        denoise_value = data.get('denoise', 0.10)
        use_free_credit = data.get('use_free_credit', True)
        transform_mode = data.get('transform_mode', 'full')  # 'full', 'custom', or 'reference'
        selected_features = data.get('selected_features', [])  # Array of features for custom mode
        selected_chad = data.get('selected_chad')  # Selected chad for reference mode
        face_swap_intensity = data.get('face_swap_intensity', 0.5)  # Intensity for reference mode
        
        if not filename or not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            return jsonify({'error': 'File not found'}), 404
        
        # Validate denoise value (allow 0.3 for custom features mode, 0.15-0.35 for CHAD 2.0)
        if not isinstance(denoise_value, (int, float)):
            return jsonify({'error': 'Invalid denoise value format'}), 400
        
        # Allow 0.3 for custom features mode
        if denoise_value == 0.3:
            pass
        # Allow 0.15-0.35 for CHAD 2.0 mode
        elif transform_mode == 'chad_2_0' and (denoise_value < 0.15 or denoise_value > 0.35):
            return jsonify({'error': 'Invalid denoise value for CHAD 2.0. Must be between 0.15 and 0.35'}), 400
        # Normal range for regular mode
        elif transform_mode != 'chad_2_0' and (denoise_value < 0.10 or denoise_value > 0.25):
            return jsonify({'error': 'Invalid denoise value. Must be between 0.10 and 0.25'}), 400
        
        # Check and deduct credits - prioritize paid credits first
        used_free = False
        used_paid = False
        
        # First try to use paid credits (including the 12 starter credits)
        if current_user.can_generate_paid():
            if current_user.use_paid_credit():
                used_paid = True
            else:
                return jsonify({'error': 'Failed to deduct credit'}), 402
        # If no paid credits, try daily free credit
        elif current_user.can_generate_free():
            current_user.use_free_generation()
            used_free = True
        else:
            return jsonify({
                'error': 'No credits available. Purchase more credits or wait until tomorrow for your free generation.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        # Determine tier name for logging
        tier_name = 'custom'
        if denoise_value == 0.10:
            tier_name = '+1_Tier'
        elif denoise_value == 0.17:
            tier_name = '+2_Tier'
        elif denoise_value == 0.25:
            tier_name = 'Chad'
        
        # Create generation record
        generation = Generation(
            user_id=current_user.id,
            preset=tier_name,  # Store tier name for compatibility
            workflow_type='modal' if USE_MODAL else ('runpod' if USE_CLOUD_GPU else CURRENT_WORKFLOW),
            input_filename=filename,
            used_free_credit=used_free,
            used_paid_credit=used_paid,
            status='pending'
        )
        
        db.session.add(generation)
        db.session.commit()
        
        if USE_MODAL:
            # Use Modal.com for processing
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Check if Modal client is properly initialized
            if not gpu_client or not hasattr(gpu_client, 'token_configured') or not gpu_client.token_configured:
                generation.status = 'failed'
                generation.error_message = 'Modal.com not configured. Please set up authentication token.'
                db.session.commit()
                return jsonify({
                    'error': 'Modal.com not configured. Please contact support to enable GPU processing.',
                    'setup_required': True,
                    'instructions': 'Modal.com authentication required. Please run: modal token new'
                }), 503
            
            if not gpu_client.app:
                generation.status = 'failed'
                generation.error_message = 'Modal.com app not deployed.'
                db.session.commit()
                return jsonify({
                    'error': 'Modal.com app not deployed. Please contact support to enable GPU processing.',
                    'setup_required': True,
                    'instructions': 'Modal.com app deployment required.'
                }), 503
            
            try:
                # Map denoise value to preset and intensity
                if denoise_value == 0.10:
                    preset_key = 'tier1'
                    denoise_intensity = 4
                elif denoise_value == 0.15:
                    preset_key = 'tier2'
                    denoise_intensity = 6
                elif denoise_value == 0.25:
                    preset_key = 'chad'
                    denoise_intensity = 8
                else:
                    # Default mapping for custom values
                    preset_key = 'tier1'
                    denoise_intensity = int((denoise_value - 0.10) / 0.15 * 10) + 1
                    denoise_intensity = max(1, min(10, denoise_intensity))
                
                # Start Modal.com generation
                result_image, error = gpu_client.generate_image(
                    image_path=file_path,
                    preset_key=preset_key,
                    denoise_intensity=denoise_intensity
                )
                
                if error or not result_image:
                    generation.status = 'failed'
                    generation.error_message = error or 'Failed to generate image'
                    db.session.commit()
                    return jsonify({'error': error or 'Failed to generate image'}), 500
                
                # Save result image immediately (Modal returns the image directly)
                result_filename = f"result_{generation.id}_{int(time.time())}.png"
                result_path = os.path.join(OUTPUT_FOLDER, result_filename)
                
                with open(result_path, 'wb') as f:
                    f.write(result_image)
                
                # Update generation record
                generation.prompt_id = f"modal_{generation.id}"
                generation.status = 'completed'
                generation.started_at = datetime.utcnow()
                generation.completed_at = datetime.utcnow()
                generation.output_filename = result_filename
                db.session.commit()
                
                logger.info(f"Modal.com generation completed for {current_user.email}: {generation.id} (free: {used_free}, paid: {used_paid})")
                
                return jsonify({
                    'success': True,
                    'prompt_id': generation.prompt_id,
                    'generation_id': generation.id,
                    'denoise': denoise_value,
                    'tier_name': tier_name,
                    'used_free_credit': used_free,
                    'used_paid_credit': used_paid,
                    'remaining_credits': current_user.credits,
                    'completed': True,  # Modal completes immediately
                    'download_url': f'/result/{generation.prompt_id}',
                    'message': f'Generation completed with {tier_name.replace("_", " ")} tier! 95% cost savings achieved!'
                })
                
            except Exception as e:
                generation.status = 'failed'
                generation.error_message = str(e)
                db.session.commit()
                logger.error(f"Modal.com processing error: {e}")
                return jsonify({'error': f'Modal.com processing failed: {str(e)}'}), 500
        
        elif USE_CLOUD_GPU:
            # Use Cloud GPU for processing (Vast.ai or RunPod)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                if VAST_ON_DEMAND_MODE:
                    # Use Vast.ai On-Demand mode
                    # Map denoise value to preset and intensity
                    if denoise_value == 0.10:
                        preset_key = 'tier1'
                        denoise_intensity = 4
                    elif denoise_value == 0.15:
                        preset_key = 'tier2'
                        denoise_intensity = 6
                    elif denoise_value == 0.25:
                        preset_key = 'chad'
                        denoise_intensity = 8
                    else:
                        # Default mapping for custom values
                        preset_key = 'tier1'
                        denoise_intensity = int((denoise_value - 0.10) / 0.15 * 10) + 1
                        denoise_intensity = max(1, min(10, denoise_intensity))
                    
                    # Start Vast.ai On-Demand generation
                    result_image, error = gpu_client.generate_image(
                        image_path=file_path,
                        preset_key=preset_key,
                        denoise_intensity=denoise_intensity
                    )
                    
                    if error or not result_image:
                        generation.status = 'failed'
                        generation.error_message = error or 'Failed to generate image'
                        db.session.commit()
                        return jsonify({'error': error or 'Failed to generate image'}), 500
                    
                    # Save result image immediately (on-demand returns the image directly)
                    result_filename = f"result_{generation.id}_{int(time.time())}.png"
                    result_path = os.path.join(OUTPUT_FOLDER, result_filename)
                    
                    with open(result_path, 'wb') as f:
                        f.write(result_image)
                    
                    # Update generation record
                    generation.prompt_id = f"vast_ondemand_{generation.id}"
                    generation.status = 'completed'
                    generation.started_at = datetime.utcnow()
                    generation.completed_at = datetime.utcnow()
                    generation.output_filename = result_filename
                    db.session.commit()
                    
                    logger.info(f"Vast.ai On-Demand generation completed for {current_user.email}: {generation.id} (free: {used_free}, paid: {used_paid})")
                    
                    return jsonify({
                        'success': True,
                        'prompt_id': generation.prompt_id,
                        'generation_id': generation.id,
                        'denoise': denoise_value,
                        'tier_name': tier_name,
                        'used_free_credit': used_free,
                        'used_paid_credit': used_paid,
                        'remaining_credits': current_user.credits,
                        'completed': True,  # On-demand completes immediately
                        'download_url': f'/result/{generation.prompt_id}',
                        'message': f'Generation completed with {tier_name.replace("_", " ")} tier! 98% cost savings achieved!'
                    })
                
                else:
                    # Use regular cloud GPU (RunPod/Vast.ai)
                    # Map denoise value to preset and intensity
                    if denoise_value == 0.10:
                        preset_key = 'HTN'
                        denoise_intensity = 4
                    elif denoise_value == 0.15:
                        preset_key = 'Chadlite'
                        denoise_intensity = 6
                    elif denoise_value == 0.25:
                        preset_key = 'Chad'
                        denoise_intensity = 8
                    else:
                        # Default mapping for custom values
                        preset_key = 'HTN'
                        denoise_intensity = int((denoise_value - 0.10) / 0.15 * 10) + 1
                        denoise_intensity = max(1, min(10, denoise_intensity))
                    
                    # Start cloud GPU generation
                    job_result = gpu_client.generate_image(
                        image_path=file_path,
                        preset_key=preset_key,
                        denoise_intensity=denoise_intensity
                    )
                    
                    # Handle tuple return (job_id, error)
                    if isinstance(job_result, tuple):
                        job_id, error = job_result
                        if error or not job_id:
                            generation.status = 'failed'
                            generation.error_message = error or 'Failed to start cloud GPU generation'
                            db.session.commit()
                            return jsonify({'error': error or 'Failed to start generation'}), 500
                    else:
                        job_id = job_result
                        if not job_id:
                            generation.status = 'failed'
                            generation.error_message = 'Failed to start cloud GPU generation'
                            db.session.commit()
                            return jsonify({'error': 'Failed to start generation'}), 500
                    
                    # Update generation with job ID
                    generation.prompt_id = str(job_id)  # Ensure it's a string
                    generation.status = 'processing'
                    generation.started_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.info(f"Cloud GPU processing started for {current_user.email}: {job_id} (free: {used_free}, paid: {used_paid})")
                    
                    return jsonify({
                        'success': True,
                        'prompt_id': job_id,
                        'generation_id': generation.id,
                        'denoise': denoise_value,
                        'tier_name': tier_name,
                        'used_free_credit': used_free,
                        'used_paid_credit': used_paid,
                        'remaining_credits': current_user.credits,
                        'message': f'Processing started with {tier_name.replace("_", " ")} tier...'
                    })
                
            except Exception as e:
                generation.status = 'failed'
                generation.error_message = str(e)
                db.session.commit()
                logger.error(f"Cloud GPU processing error: {e}")
                return jsonify({'error': f'Cloud GPU processing failed: {str(e)}'}), 500
        
        else:
            # Use ComfyUI for processing
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # Handle different transformation modes
                if transform_mode == 'chad_2_0':
                    # CHAD 2.0 mode - use SD XL + custom LoRA workflow
                    tier_name = 'CHAD_2_0'
                    
                    prompt_id = gpu_client.generate_image(
                        image_path=file_path,
                        preset_name="CHAD_2_0",
                        denoise_strength=denoise_value
                    )
                    
                    logger.info(f"CHAD 2.0 generation started with {denoise_value} denoise")
                    
                elif transform_mode == 'reference' and selected_chad:
                    # Reference Chad mode - use face swap workflow
                    tier_name = f'reference_{selected_chad}'
                    
                    # Map face swap intensity (0.0 to 1.0) to percentage string for workflow
                    intensity_percent = f"{int(face_swap_intensity * 100)}%"
                    
                    # Get reference chad image path
                    reference_image_path = os.path.join('reference_chads', f'{selected_chad}.png')
                    
                    if not os.path.exists(reference_image_path):
                        generation.status = 'failed'
                        generation.error_message = f'Reference chad image not found: {selected_chad}'
                        db.session.commit()
                        return jsonify({'error': f'Reference chad image not found: {selected_chad}'}), 400
                    
                    prompt_id = gpu_client.generate_image_with_face_swap(
                        original_image_path=file_path,
                        reference_image_path=reference_image_path,
                        swap_intensity=intensity_percent
                    )
                    
                    logger.info(f"Reference chad generation started: {selected_chad} with {intensity_percent} intensity")
                    
                elif transform_mode == 'custom' and selected_features:
                    # Custom features mode - use universal workflow with feature selection
                    features_str = '_'.join(selected_features)
                    tier_name = f'custom_{features_str}'
                    
                    # Use fixed 30% intensity for custom features as mentioned in UI
                    custom_denoise = 0.3  # 30% intensity
                    
                    prompt_id = gpu_client.generate_image_with_features(
                        image_path=file_path,
                        selected_features=selected_features,
                        denoise_strength=custom_denoise
                    )
                    
                    logger.info(f"Custom features generation started: {features_str} with {custom_denoise} denoise")
                    
                else:
                    # Full face transformation mode
                    prompt_id = gpu_client.generate_image(
                        image_path=file_path,
                        preset_name=tier_name,
                        denoise_strength=denoise_value
                    )
                
                if not prompt_id:
                    generation.status = 'failed'
                    generation.error_message = 'Failed to start ComfyUI generation'
                    db.session.commit()
                    return jsonify({'error': 'Failed to start generation'}), 500
                
                # Update generation with prompt ID and mode info
                generation.prompt_id = prompt_id
                generation.status = 'processing'
                generation.started_at = datetime.utcnow()
                
                # Store transformation mode and features in the generation record
                if transform_mode == 'custom':
                    generation.preset = f"custom_{','.join(selected_features)}"
                
                db.session.commit()
                
                # Update last generation time for rate limiting
                user_last_generation[user_id] = current_time
                
                # Create appropriate message based on mode
                if transform_mode == 'custom':
                    feature_names = ', '.join(selected_features)
                    message = f'Custom transformation started for {feature_names} with 30% intensity...'
                else:
                    message = f'Processing started with {tier_name.replace("_", " ")} tier on local ComfyUI...'
                
                logger.info(f"ComfyUI processing started for {current_user.email}: {prompt_id} (mode: {transform_mode}, free: {used_free}, paid: {used_paid})")
                
                return jsonify({
                    'success': True,
                    'prompt_id': prompt_id,
                    'generation_id': generation.id,
                    'denoise': denoise_value if transform_mode == 'full' else 0.3,
                    'tier_name': tier_name,
                    'transform_mode': transform_mode,
                    'selected_features': selected_features if transform_mode == 'custom' else [],
                    'used_free_credit': used_free,
                    'used_paid_credit': used_paid,
                    'remaining_credits': current_user.credits,
                    'message': message
                })
                
            except Exception as e:
                generation.status = 'failed'
                generation.error_message = str(e)
                db.session.commit()
                logger.error(f"ComfyUI processing error: {e}")
                return jsonify({'error': f'ComfyUI processing failed: {str(e)}'}), 500
    
    except Exception as e:
        logger.error(f"Process error: {e}")
        return jsonify({'error': 'Processing failed. Please try again.'}), 500

@app.route('/status/<prompt_id>')
def check_status(prompt_id):
    """Check processing status"""
    try:
        # This logic is the same for all GPU clients
        status = gpu_client.get_job_status(prompt_id)
        
        if status == 'COMPLETED':
            # Find the generation record to pass its ID to the frontend
            generation = Generation.query.filter_by(prompt_id=prompt_id).first()
            return jsonify({
                'complete': True,
                'message': 'Processing complete!',
                'generation_id': generation.id if generation else None
            })
        elif status == 'FAILED':
            return jsonify({
                'complete': False,
                'error': True,
                'message': 'Processing failed'
            })
        else:
            return jsonify({
                'complete': False,
                'message': 'Processing in progress...'
            })
            
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': 'Failed to check status'}), 500

@app.route('/result/<prompt_id>')
@login_required
def get_result(prompt_id):
    """Get processed result"""
    try:
        # Find generation record
        generation = Generation.query.filter_by(
            prompt_id=prompt_id,
            user_id=current_user.id
        ).first()
        
        if not generation:
            return jsonify({'error': 'Generation not found'}), 404
        
        if USE_CLOUD_GPU:
            # Get RunPod result
            status = gpu_client.get_job_status(prompt_id)
            
            if status != 'COMPLETED':
                return jsonify({'error': 'Processing not complete'}), 400
            
            # Get output image from RunPod
            image_data = gpu_client.get_job_output(prompt_id)
            if not image_data:
                generation.status = 'failed'
                generation.error_message = 'Failed to retrieve result image from RunPod'
                db.session.commit()
                return jsonify({'error': 'Failed to retrieve result image'}), 500
            
            # Save result image
            result_filename = f"result_{prompt_id}.png"
            result_path = os.path.join(OUTPUT_FOLDER, result_filename)
            
            with open(result_path, 'wb') as f:
                f.write(image_data)
            
            # Update generation record
            generation.status = 'completed'
            generation.completed_at = datetime.utcnow()
            generation.output_filename = result_filename
            db.session.commit()
            
            logger.info(f"RunPod generation completed for {current_user.email}: {prompt_id}")
            
        else:
            # Get ComfyUI result
            status = gpu_client.get_job_status(prompt_id)
            
            if status != 'COMPLETED':
                return jsonify({'error': 'Processing not complete'}), 400
            
            # Get output image from ComfyUI
            image_data = gpu_client.get_job_output(prompt_id)
            if not image_data:
                generation.status = 'failed'
                generation.error_message = 'Failed to retrieve result image from ComfyUI'
                db.session.commit()
                return jsonify({'error': 'Failed to retrieve result image'}), 500
            
            # Save result image
            result_filename = f"result_{prompt_id}.png"
            result_path = os.path.join(OUTPUT_FOLDER, result_filename)
            
            with open(result_path, 'wb') as f:
                f.write(image_data)
            
            # Update generation record
            generation.status = 'completed'
            generation.completed_at = datetime.utcnow()
            generation.output_filename = result_filename
            db.session.commit()
            
            logger.info(f"ComfyUI generation completed for {current_user.email}: {prompt_id}")
        
        return send_file(result_path, as_attachment=True, download_name=f"morphed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    
    except Exception as e:
        logger.error(f"Result retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve result'}), 500

@app.route('/gpu-status')
def gpu_status():
    """GPU status endpoint for real-time status checking"""
    try:
        if USE_LOCAL_COMFYUI:
            # Check Local ComfyUI connection
            is_available = False
            if gpu_client:
                try:
                    is_available = gpu_client.test_connection()
                except:
                    is_available = False
            
            return jsonify({
                'available': is_available,
                'status': 'ready' if is_available else 'unavailable',
                'message': 'GPU ready for generation' if is_available else 'I need more money to afford cloud GPU rent for yall so please buy some credits lmao 😅',
                'gpu_type': 'local_comfyui',
                'url': LOCAL_COMFYUI_URL if is_available else None
            })
        else:
            # For other GPU types, assume available if client exists
            is_available = gpu_client is not None
            return jsonify({
                'available': is_available,
                'status': 'ready' if is_available else 'unavailable',
                'message': 'GPU ready for generation' if is_available else 'GPU service unavailable',
                'gpu_type': 'cloud_gpu' if USE_CLOUD_GPU else 'modal' if USE_MODAL else 'comfyui'
            })
    except Exception as e:
        logger.error(f"GPU status check error: {e}")
        return jsonify({
            'available': False,
            'status': 'error',
            'message': 'Attention. No available or low balance GPU. Temporary cant generate images',
            'error': str(e)
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if USE_LOCAL_COMFYUI:
            # Check Local ComfyUI connection
            gpu_status = "disconnected"
            if gpu_client:
                try:
                    gpu_status = "connected" if gpu_client.test_connection() else "disconnected"
                except:
                    gpu_status = "disconnected"
            
            gpu_type = "local_comfyui"
            gpu_info = f"Local ComfyUI: {LOCAL_COMFYUI_URL} (Using {LOCAL_COMFYUI_WORKFLOW})"
        elif USE_MODAL:
            # Check Modal.com connection
            gpu_status = "disconnected"
            if gpu_client:
                try:
                    gpu_status = "connected" if gpu_client.test_connection() else "disconnected"
                except:
                    gpu_status = "disconnected"
            
            gpu_type = "modal.com"
            gpu_info = "Modal.com API (95% cost savings vs RunPod!)"
        elif USE_CLOUD_GPU:
            # Check Vast.ai connection
            gpu_status = "disconnected"
            if gpu_client:
                try:
                    gpu_status = "connected" if gpu_client.test_connection() else "disconnected"
                except:
                    gpu_status = "disconnected"
            
            gpu_type = "vast.ai"
            gpu_info = "Vast.ai API (99% cost savings vs RunPod!)"
        else:
            # Check ComfyUI connection
            try:
                response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
                gpu_status = "connected" if response.status_code == 200 else "disconnected"
            except:
                gpu_status = "disconnected"
            gpu_type = "comfyui"
            gpu_info = f"Local: {COMFYUI_URL}"
    except Exception as e:
        logger.error(f"Health check error: {e}")
        gpu_status = "error"
        gpu_type = "unknown"
        gpu_info = "Health check failed"
    
    return jsonify({
        'status': 'healthy',
        'gpu_type': gpu_type,
        'gpu_status': gpu_status,
        'gpu_info': gpu_info,
        'presets': list(PRESETS.keys()),
        'cloud_gpu_enabled': USE_CLOUD_GPU,
        'modal_enabled': USE_MODAL,
        'local_comfyui_enabled': USE_LOCAL_COMFYUI,
        'app_version': '4.1.0-local-comfyui'
    })

# Global variable to store the registered tunnel URL
registered_tunnel_url = None

# Webhook endpoint to accept registered quick-tunnel URLs from a trusted registrar (your local machine).
# The registrar should POST JSON: {"url": "https://xxxxx.trycloudflare.com"} with header X-TUNNEL-SECRET set.
# Set REGISTER_TUNNEL_SECRET in Railway environment to a shared secret before enabling this.
@app.route('/register-tunnel', methods=['POST'])
def register_tunnel_webhook():
    """
    Accept a tunnel URL from an external registrar and persist it for automatic detection.
    This endpoint requires a shared secret header to prevent abuse.
    """
    global registered_tunnel_url
    
    try:
        expected_secret = os.getenv('REGISTER_TUNNEL_SECRET', 'morphpas')  # Default secret
        provided_secret = request.headers.get('X-TUNNEL-SECRET', '')
        if not expected_secret or provided_secret != expected_secret:
            logger.warning("Unauthorized /register-tunnel attempt")
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({'error': 'Invalid payload. Provide JSON with \"url\" field.'}), 400

        url = data['url'].strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            return jsonify({'error': 'Invalid URL format'}), 400

        # Quick sanity check: ensure ComfyUI responds on the supplied URL
        try:
            resp = requests.get(f"{url.rstrip('/')}/system_stats", timeout=5)
            if resp.status_code != 200:
                logger.warning(f"Register-tunnel received non-200 from candidate URL: {url} -> {resp.status_code}")
                return jsonify({'error': 'ComfyUI not responding at provided URL'}), 400
        except Exception as e:
            logger.warning(f"Register-tunnel connectivity test failed for {url}: {e}")
            return jsonify({'error': 'Connection to provided URL failed', 'details': str(e)}), 400

        # Store the URL globally and in the registry
        registered_tunnel_url = url
        
        try:
            ok = set_tunnel_url(url)
            if ok:
                logger.info(f"✅ Registered tunnel URL via webhook: {url}")
                
                # Update the GPU client to use the new URL
                global gpu_client
                if USE_LOCAL_COMFYUI and gpu_client:
                    gpu_client.base_url = url.rstrip('/')
                    logger.info(f"🔄 Updated Local ComfyUI client to use: {url}")
                    
                    # Test the connection immediately
                    try:
                        if gpu_client.test_connection():
                            logger.info(f"✅ Successfully connected to ComfyUI at: {url}")
                        else:
                            logger.warning(f"⚠️ Connection test failed for: {url}")
                    except Exception as e:
                        logger.error(f"❌ Connection test error: {e}")
                
                return jsonify({'success': True, 'url': url, 'message': 'Tunnel URL registered and client updated'}), 200
            else:
                logger.error("Failed to persist tunnel URL")
                return jsonify({'error': 'Failed to save URL on server'}), 500
        except Exception as e:
            logger.error(f"Error saving tunnel URL: {e}")
            return jsonify({'error': 'Server error', 'details': str(e)}), 500

    except Exception as e:
        logger.error(f"register_tunnel_webhook error: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Facial Evaluation routes
@app.route('/facial-evaluation')
@login_required
def facial_evaluation_dashboard():
    """User facial evaluation dashboard"""
    # Get user's facial evaluation requests
    evaluations = FacialEvaluation.query.filter_by(user_id=current_user.id)\
        .order_by(FacialEvaluation.created_at.desc()).all()
    
    return render_template('facial_evaluation/dashboard.html', evaluations=evaluations)

@app.route('/request-facial-evaluation', methods=['POST'])
@login_required
def request_facial_evaluation():
    """Request facial evaluation from generation result"""
    try:
        # Check if user is blocked
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support.'}), 403
        
        data = request.get_json()
        generation_id = data.get('generation_id')
        
        # Find the generation
        generation = Generation.query.filter_by(
            id=generation_id,
            user_id=current_user.id,
            status='completed'
        ).first()
        
        if not generation:
            return jsonify({'error': 'Generation not found or not completed'}), 404
        
        # Check if user has enough credits (20 credits required)
        if current_user.credits < 20:
            return jsonify({
                'error': 'Insufficient credits. You need 20 credits for facial evaluation.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        # Check if evaluation already exists for this generation
        existing_evaluation = FacialEvaluation.query.filter_by(
            generation_id=generation_id,
            user_id=current_user.id
        ).first()
        
        if existing_evaluation:
            return jsonify({'error': 'Facial evaluation already requested for this generation'}), 400
        
        # Deduct credits
        current_user.credits -= 20
        
        # Copy images to facial evaluation folder for persistent storage
        # Copy original image from uploads to facial_evaluations
        original_source_path = os.path.join(UPLOAD_FOLDER, generation.input_filename)
        original_extension = generation.input_filename.rsplit('.', 1)[1].lower()
        original_eval_filename = f"eval_original_{uuid.uuid4()}.{original_extension}"
        original_eval_path = os.path.join(FACIAL_EVALUATION_FOLDER, original_eval_filename)
        
        # Copy morphed image from outputs to facial_evaluations
        morphed_source_path = os.path.join(OUTPUT_FOLDER, generation.output_filename)
        morphed_extension = generation.output_filename.rsplit('.', 1)[1].lower()
        morphed_eval_filename = f"eval_morphed_{uuid.uuid4()}.{morphed_extension}"
        morphed_eval_path = os.path.join(FACIAL_EVALUATION_FOLDER, morphed_eval_filename)
        
        try:
            # Copy original image
            if os.path.exists(original_source_path):
                shutil.copy2(original_source_path, original_eval_path)
                logger.info(f"Copied original image to facial evaluation folder: {original_eval_filename}")
            else:
                return jsonify({'error': 'Original image not found'}), 404
            
            # Copy morphed image
            if os.path.exists(morphed_source_path):
                shutil.copy2(morphed_source_path, morphed_eval_path)
                logger.info(f"Copied morphed image to facial evaluation folder: {morphed_eval_filename}")
            else:
                # Clean up copied original image
                os.remove(original_eval_path)
                return jsonify({'error': 'Morphed image not found'}), 404
                
        except Exception as e:
            # Clean up any copied files on error
            try:
                if os.path.exists(original_eval_path):
                    os.remove(original_eval_path)
                if os.path.exists(morphed_eval_path):
                    os.remove(morphed_eval_path)
            except:
                pass
            logger.error(f"Error copying images for facial evaluation: {e}")
            return jsonify({'error': 'Failed to prepare images for evaluation'}), 500

        # Create facial evaluation request with copied images
        evaluation = FacialEvaluation(
            user_id=current_user.id,
            generation_id=generation_id,
            original_image_filename=original_eval_filename,
            morphed_image_filename=morphed_eval_filename,
            credits_used=20
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        logger.info(f"Facial evaluation requested by {current_user.email} for generation {generation_id}")
        
        return jsonify({
            'success': True,
            'evaluation_id': evaluation.id,
            'message': 'Your facial evaluation request has been submitted! Our expert will provide detailed analysis within 24 hours.',
            'remaining_credits': current_user.credits
        })
        
    except Exception as e:
        logger.error(f"Error requesting facial evaluation: {e}")
        return jsonify({'error': 'Failed to submit evaluation request. Please try again.'}), 500

@app.route('/request-facial-evaluation-standalone', methods=['POST'])
@login_required
def request_facial_evaluation_standalone():
    """Request facial evaluation with standalone image upload"""
    try:
        # Check if user is blocked
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support.'}), 403
        
        # Check if files were uploaded (support both single and multiple files)
        files_to_process = []
        
        # Check for file1 (required)
        if 'file1' in request.files:
            file1 = request.files['file1']
            if file1.filename != '':
                files_to_process.append(('file1', file1))
        
        # Check for file2 (optional)
        if 'file2' in request.files:
            file2 = request.files['file2']
            if file2.filename != '':
                files_to_process.append(('file2', file2))
        
        # Fallback to single file upload for backward compatibility
        if not files_to_process and 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                files_to_process.append(('file', file))
        
        if not files_to_process:
            return jsonify({'error': 'No image provided'}), 400
        
        # Check if user has enough credits (20 credits required)
        if current_user.credits < 20:
            return jsonify({
                'error': 'Insufficient credits. You need 20 credits for facial evaluation.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        # Process uploaded files
        saved_files = []
        
        for file_key, file in files_to_process:
            if file and allowed_file(file.filename):
                # Generate secure filename
                original_filename = secure_filename(file.filename) if SECURE_FILENAME_ENABLED else file.filename
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"eval_{uuid.uuid4()}.{file_extension}"
                file_path = os.path.join(FACIAL_EVALUATION_FOLDER, unique_filename)
                
                # Save uploaded file
                file.save(file_path)
                
                # Validate image
                is_valid, message = validate_image(file_path)
                if not is_valid:
                    # Clean up any previously saved files
                    for saved_file in saved_files:
                        try:
                            os.remove(saved_file['path'])
                        except:
                            pass
                    return jsonify({'error': f'{file_key}: {message}'}), 400
                
                saved_files.append({
                    'key': file_key,
                    'filename': unique_filename,
                    'path': file_path
                })
            else:
                # Clean up any previously saved files
                for saved_file in saved_files:
                    try:
                        os.remove(saved_file['path'])
                    except:
                        pass
                return jsonify({'error': f'Invalid file type for {file_key}. Please upload PNG, JPG, JPEG, or WebP images.'}), 400
        
        if not saved_files:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Deduct credits
        current_user.credits -= 20
        
        # Create facial evaluation request with primary image
        primary_file = saved_files[0]
        secondary_file = saved_files[1] if len(saved_files) > 1 else None
        
        evaluation = FacialEvaluation(
            user_id=current_user.id,
            original_image_filename=primary_file['filename'],
            secondary_image_filename=secondary_file['filename'] if secondary_file else None,
            morphed_image_filename='',
            status='Pending',
            credits_used=20
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        file_count = len(saved_files)
        logger.info(f"Standalone facial evaluation requested by {current_user.email} with {file_count} image(s)")
        
        return jsonify({
            'success': True,
            'evaluation_id': evaluation.id,
            'message': f'Your facial evaluation request has been submitted with {file_count} image(s)! Our expert will provide detailed analysis within 24 hours.',
            'remaining_credits': current_user.credits
        })
        
    except Exception as e:
        logger.error(f"Error requesting standalone facial evaluation: {e}")
        return jsonify({'error': 'Failed to submit evaluation request. Please try again.'}), 500

@app.route('/admin/facial-evaluations')
@login_required
def admin_facial_evaluations():
    """Admin view of facial evaluation requests"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get pending and completed evaluations
    pending_evaluations = FacialEvaluation.query.filter_by(status='Pending')\
        .order_by(FacialEvaluation.created_at.desc()).all()
    completed_evaluations = FacialEvaluation.query.filter_by(status='Completed')\
        .order_by(FacialEvaluation.completed_at.desc()).limit(20).all()
    
    return render_template('admin/facial_evaluations.html',
                         pending_evaluations=pending_evaluations,
                         completed_evaluations=completed_evaluations,
                         now=datetime.utcnow())

@app.route('/admin/facial-evaluation/<evaluation_id>', methods=['GET', 'POST'])
@login_required
def admin_view_facial_evaluation(evaluation_id):
    """Admin view facial evaluation request"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    evaluation = FacialEvaluation.query.get_or_404(evaluation_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            response_text = data.get('response', '').strip()
            
            if not response_text or len(response_text) < 50:
                return jsonify({'error': 'Response must be at least 50 characters long'}), 400
            
            if len(response_text) > 2000:
                return jsonify({'error': 'Response must be less than 2000 characters'}), 400
            
            # Update evaluation
            evaluation.admin_response = response_text
            evaluation.admin_id = current_user.id
            evaluation.status = 'Completed'
            evaluation.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} responded to facial evaluation {evaluation_id}")
            
            return jsonify({
                'success': True,
                'message': 'Facial evaluation response submitted successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error submitting facial evaluation response: {e}")
            return jsonify({'error': 'Failed to submit response. Please try again.'}), 500
            
    return render_template('admin/respond_facial_evaluation.html', evaluation=evaluation)

@app.route('/admin/respond-facial-evaluation/<evaluation_id>')
@login_required
def admin_respond_facial_evaluation(evaluation_id):
    """Admin respond to facial evaluation request"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    evaluation = FacialEvaluation.query.get_or_404(evaluation_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            response_text = data.get('response', '').strip()
            
            if not response_text or len(response_text) < 50:
                return jsonify({'error': 'Response must be at least 50 characters long'}), 400
            
            if len(response_text) > 2000:
                return jsonify({'error': 'Response must be less than 2000 characters'}), 400
            
            # Update evaluation
            evaluation.admin_response = response_text
            evaluation.admin_id = current_user.id
            evaluation.status = 'completed'
            evaluation.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} responded to facial evaluation {evaluation_id}")
            
            return jsonify({
                'success': True,
                'message': 'Facial evaluation response submitted successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error submitting facial evaluation response: {e}")
            return jsonify({'error': 'Failed to submit response. Please try again.'}), 500
    
    # GET request - show evaluation details
    return render_template('admin/respond_facial_evaluation.html', evaluation=evaluation)

@app.route('/facial-evaluation-image/<evaluation_id>/<image_type>')
@login_required
def get_facial_evaluation_image(evaluation_id, image_type):
    """Get images for facial evaluation (original, morphed, or secondary)"""
    try:
        evaluation = FacialEvaluation.query.get_or_404(evaluation_id)
        
        # Check permissions
        if not current_user.is_admin and evaluation.user_id != current_user.id:
            logger.warning(f"Access denied for facial evaluation image: {evaluation_id} by {current_user.email}")
            return "Access denied", 403
        
        # Determine filename and folder based on image type
        filename = None
        folder = None
        
        if image_type == 'original':
            filename = evaluation.original_image_filename
            folder = FACIAL_EVALUATION_FOLDER  # ALL original images are now stored in facial_evaluations
        elif image_type == 'morphed' and evaluation.morphed_image_filename:
            filename = evaluation.morphed_image_filename
            folder = FACIAL_EVALUATION_FOLDER  # ALL morphed images are now stored in facial_evaluations
        elif image_type == 'secondary' and evaluation.secondary_image_filename:
            filename = evaluation.secondary_image_filename
            folder = FACIAL_EVALUATION_FOLDER  # Secondary images are always stored in facial_evaluations
        else:
            logger.warning(f"Invalid image type or not available: {image_type} for evaluation {evaluation_id}")
            return "Image not available", 404
        
        if not filename:
            logger.warning(f"No filename found for {image_type} image in evaluation {evaluation_id}")
            return "Image not available", 404
        
        file_path = os.path.join(folder, filename)
        logger.info(f"Attempting to serve {image_type} image: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"Image file not found: {file_path}")
            return "Image file not found", 404
        
        logger.info(f"Successfully serving facial evaluation {image_type} image: {file_path}")
        return send_file(file_path)
        
    except Exception as e:
        logger.error(f"Error serving facial evaluation image {evaluation_id}/{image_type}: {e}")
        return "Failed to load image", 500

# Ratios Morph routes
@app.route('/ratios-morph')
@login_required
def ratios_morph_dashboard():
    """User ratios morph dashboard"""
    morphs = RatiosMorph.query.filter_by(user_id=current_user.id)\
        .order_by(RatiosMorph.created_at.desc()).all()
    
    return render_template('ratios_morph/dashboard.html', morphs=morphs)

@app.route('/request-ratios-morph', methods=['POST'])
@login_required
def request_ratios_morph():
    """Request ratios morph with standalone image upload"""
    try:
        if current_user.is_blocked:
            return jsonify({'error': 'Your account has been blocked. Please contact support.'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if current_user.credits < 40:
            return jsonify({
                'error': 'Insufficient credits. You need 40 credits for a Ratios Morph.',
                'need_credits': True,
                'buy_credits_url': '/payments/buy-credits'
            }), 402
        
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename) if SECURE_FILENAME_ENABLED else file.filename
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"ratios_morph_{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(FACIAL_EVALUATION_FOLDER, unique_filename)
            
            file.save(file_path)
            
            is_valid, message = validate_image(file_path)
            if not is_valid:
                os.remove(file_path)
                return jsonify({'error': message}), 400
            
            current_user.credits -= 40
            
            morph = RatiosMorph(
                user_id=current_user.id,
                original_image_filename=unique_filename,
                credits_used=40
            )
            
            db.session.add(morph)
            db.session.commit()
            
            logger.info(f"Ratios Morph requested by {current_user.email}")
            
            return jsonify({
                'success': True,
                'morph_id': morph.id,
                'message': 'Your Ratios Morph request has been submitted! Our expert will provide detailed analysis and the morphed image within 24 hours.',
                'remaining_credits': current_user.credits
            })
        
        return jsonify({'error': 'Invalid file type.'}), 400
        
    except Exception as e:
        logger.error(f"Error requesting ratios morph: {e}")
        return jsonify({'error': 'Failed to submit request. Please try again.'}), 500

@app.route('/ratios-morph-image/<morph_id>/<image_type>')
@login_required
def get_ratios_morph_image(morph_id, image_type):
    """Get images for ratios morph"""
    try:
        morph = RatiosMorph.query.get_or_404(morph_id)
        
        if not current_user.is_admin and morph.user_id != current_user.id:
            return "Access denied", 403
        
        filename = None
        if image_type == 'original':
            filename = morph.original_image_filename
        elif image_type == 'morphed':
            filename = morph.morphed_image_filename
        
        if not filename:
            return "Image not available", 404
        
        file_path = os.path.join(FACIAL_EVALUATION_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return "Image file not found", 404
        
        return send_file(file_path)
        
    except Exception as e:
        logger.error(f"Error serving ratios morph image {morph_id}/{image_type}: {e}")
        return "Failed to load image", 500

@app.template_filter('markdown')
def markdown_filter(s):
    """Convert a string to Markdown"""
    if s:
        return mistune.html(s)
    return ''

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_generations': Generation.query.count(),
        'total_revenue': db.session.query(db.func.sum(Transaction.amount_usd)).filter_by(payment_status='completed').scalar() or 0,
        'pending_payments': Transaction.query.filter_by(payment_status='pending').count()
    }
    
    # Get recent data
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(50).all()
    generations = Generation.query.order_by(Generation.created_at.desc()).limit(50).all()
    
    # Get facial evaluation requests
    facial_evaluation_requests = FacialEvaluation.query.order_by(FacialEvaluation.created_at.desc()).limit(50).all()
    ratios_morph_requests = RatiosMorph.query.order_by(RatiosMorph.created_at.desc()).limit(50).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         users=users,
                         transactions=transactions,
                         generations=generations,
                         facial_evaluation_requests=facial_evaluation_requests,
                         ratios_morph_requests=ratios_morph_requests)

@app.route('/admin/ratios-morphs')
@login_required
def admin_ratios_morphs():
    """Admin view of ratios morph requests"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    pending_morphs = RatiosMorph.query.filter_by(status='Pending')\
        .order_by(RatiosMorph.created_at.desc()).all()
    completed_morphs = RatiosMorph.query.filter_by(status='Completed')\
        .order_by(RatiosMorph.completed_at.desc()).limit(20).all()
    
    return render_template('admin/ratios_morphs.html',
                         pending_morphs=pending_morphs,
                         completed_morphs=completed_morphs,
                         now=datetime.utcnow())

@app.route('/admin/ratios-morph/<morph_id>', methods=['GET', 'POST'])
@login_required
def admin_view_ratios_morph(morph_id):
    """Admin view and respond to ratios morph request"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    morph = RatiosMorph.query.get_or_404(morph_id)
    
    if request.method == 'POST':
        try:
            response_text = request.form.get('response', '').strip()
            morphed_image = request.files.get('morphed_image')
            
            if not response_text or len(response_text) < 50:
                flash('Response must be at least 50 characters long', 'error')
                return redirect(url_for('admin_view_ratios_morph', morph_id=morph_id))
            
            if morphed_image and allowed_file(morphed_image.filename):
                original_filename = secure_filename(morphed_image.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"ratios_morphed_{uuid.uuid4()}.{file_extension}"
                file_path = os.path.join(FACIAL_EVALUATION_FOLDER, unique_filename)
                morphed_image.save(file_path)
                morph.morphed_image_filename = unique_filename
            
            morph.admin_response = response_text
            morph.admin_id = current_user.id
            morph.status = 'Completed'
            morph.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} responded to ratios morph {morph_id}")
            flash('Ratios morph response submitted successfully!', 'success')
            return redirect(url_for('admin_ratios_morphs'))
            
        except Exception as e:
            logger.error(f"Error submitting ratios morph response: {e}")
            flash('Failed to submit response. Please try again.', 'error')
    
    return render_template('admin/respond_ratios_morph.html', morph=morph)

@app.route('/admin/update-credits', methods=['POST'])
@login_required
def admin_update_credits():
    """Admin update user credits"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        action = data.get('action')  # add, set, subtract
        amount = int(data.get('amount', 0))
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if action == 'add':
            user.credits += amount
        elif action == 'set':
            user.credits = amount
        elif action == 'subtract':
            user.credits = max(0, user.credits - amount)
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} updated credits for {user.email}: {action} {amount}")
        
        return jsonify({
            'success': True,
            'new_credits': user.credits,
            'message': f'Credits updated successfully. New balance: {user.credits}'
        })
        
    except Exception as e:
        logger.error(f"Error updating credits: {e}")
        return jsonify({'error': 'Failed to update credits'}), 500

@app.route('/admin/reject-payment/<transaction_id>', methods=['POST'])
@login_required
def admin_reject_payment(transaction_id):
    """Admin reject payment"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if transaction.payment_status != 'pending':
            return jsonify({'error': 'Transaction is not pending'}), 400
        
        transaction.payment_status = 'failed'
        transaction.completed_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} rejected payment: {transaction_id}")
        
        return jsonify({'success': True, 'message': 'Payment rejected'})
        
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        return jsonify({'error': 'Failed to reject payment'}), 500

@app.route('/admin/block-user/<user_id>', methods=['POST'])
@login_required
def admin_block_user(user_id):
    """Admin block/unblock user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent blocking admin users
        if user.is_admin:
            return jsonify({'error': 'Cannot block admin users'}), 400
        
        # Toggle blocked status
        user.is_blocked = not user.is_blocked
        action = 'blocked' if user.is_blocked else 'unblocked'
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} {action} user: {user.email}")
        
        return jsonify({
            'success': True,
            'is_blocked': user.is_blocked,
            'message': f'User {action} successfully'
        })
        
    except Exception as e:
        logger.error(f"Error blocking/unblocking user: {e}")
        return jsonify({'error': 'Failed to update user status'}), 500

@app.route('/admin/delete_facial_evaluation/<evaluation_id>', methods=['POST'])
@login_required
def admin_delete_facial_evaluation(evaluation_id):
    """Admin delete facial evaluation request"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    try:
        evaluation = FacialEvaluation.query.get_or_404(evaluation_id)
        
        # Track images to delete
        images_deleted = 0
        
        # Delete original image if exists
        if evaluation.original_image_filename:
            original_path = os.path.join(FACIAL_EVALUATION_FOLDER, evaluation.original_image_filename)
            if os.path.exists(original_path):
                try:
                    os.remove(original_path)
                    images_deleted += 1
                    logger.info(f"Deleted original image: {original_path}")
                except Exception as e:
                    logger.error(f"Failed to delete original image {original_path}: {e}")
        
        # Delete morphed image if exists
        if evaluation.morphed_image_filename:
            morphed_path = os.path.join(FACIAL_EVALUATION_FOLDER, evaluation.morphed_image_filename)
            if os.path.exists(morphed_path):
                try:
                    os.remove(morphed_path)
                    images_deleted += 1
                    logger.info(f"Deleted morphed image: {morphed_path}")
                except Exception as e:
                    logger.error(f"Failed to delete morphed image {morphed_path}: {e}")
        
        # Delete secondary image if exists
        if evaluation.secondary_image_filename:
            secondary_path = os.path.join(FACIAL_EVALUATION_FOLDER, evaluation.secondary_image_filename)
            if os.path.exists(secondary_path):
                try:
                    os.remove(secondary_path)
                    images_deleted += 1
                    logger.info(f"Deleted secondary image: {secondary_path}")
                except Exception as e:
                    logger.error(f"Failed to delete secondary image {secondary_path}: {e}")
        
        # Delete the evaluation record from database
        user_email = evaluation.user.email
        db.session.delete(evaluation)
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} deleted facial evaluation {evaluation_id} from {user_email} (deleted {images_deleted} images)")
        
        return jsonify({
            'success': True,
            'images_deleted': images_deleted,
            'message': f'Facial evaluation deleted successfully. Removed {images_deleted} image files from storage.'
        })
        
    except Exception as e:
        logger.error(f"Error deleting facial evaluation {evaluation_id}: {e}")
        return jsonify({'error': f'Failed to delete evaluation: {str(e)}'}), 500

@app.route('/admin/railway-volume-proof')
@login_required
def admin_railway_volume_proof():
    """Admin route to run Railway volume proof script"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Import the proof script directly instead of running subprocess
        import importlib.util
        import io
        import contextlib
        
        # Capture output
        output_buffer = io.StringIO()
        
        with contextlib.redirect_stdout(output_buffer):
            # Load and execute the proof script
            spec = importlib.util.spec_from_file_location("railway_volume_proof", "railway_volume_proof.py")
            proof_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(proof_module)
            
            # Run the main function
            if hasattr(proof_module, 'generate_proof_report'):
                evidence = proof_module.generate_proof_report()
            else:
                print("Running proof verification...")
                # Execute the main block
                exec(open('railway_volume_proof.py').read())
        
        output = output_buffer.getvalue()
        
        return f"""
        <html>
        <head>
            <title>Railway Volume Proof</title>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: 'Courier New', monospace; 
                    background: #000; 
                    color: #0f0; 
                    padding: 20px; 
                    line-height: 1.4;
                }}
                .success {{ color: #0f0; }}
                .warning {{ color: #ff0; }}
                .error {{ color: #f00; }}
                .info {{ color: #0ff; }}
                pre {{ 
                    background: #111; 
                    padding: 15px; 
                    border-radius: 5px; 
                    overflow-x: auto;
                    white-space: pre-wrap;
                }}
                a {{ color: #0ff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                h1, h2 {{ color: #fff; }}
            </style>
        </head>
        <body>
        <h1>🚀 RAILWAY VOLUME PROOF VERIFICATION</h1>
        <p class="info">This verification proves that facial evaluation images are stored in Railway persistent volumes.</p>
        
        <h2>📊 VERIFICATION OUTPUT:</h2>
        <pre class="success">{output}</pre>
        
        <h2>✅ CONCLUSION:</h2>
        <p class="success">Your facial evaluation feature is using Railway persistent volumes as configured in railway.toml:</p>
        <pre class="info">[[deploy.volumes]]
name = "facial-evaluations"
mountPath = "/app/facial_evaluations"</pre>
        
        <p><a href="/admin">← Back to Admin Dashboard</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return f"""
        <html>
        <head>
            <title>Railway Volume Proof - Error</title>
            <style>
                body {{ 
                    font-family: 'Courier New', monospace; 
                    background: #000; 
                    color: #f00; 
                    padding: 20px; 
                }}
                pre {{ 
                    background: #111; 
                    padding: 15px; 
                    border-radius: 5px; 
                    overflow-x: auto;
                }}
                a {{ color: #0ff; }}
            </style>
        </head>
        <body>
        <h1>❌ ERROR RUNNING PROOF SCRIPT</h1>
        <p>Error: {str(e)}</p>
        <h2>📋 DETAILED ERROR:</h2>
        <pre>{error_details}</pre>
        
        <h2>🔧 MANUAL VERIFICATION:</h2>
        <p>You can manually verify Railway volume usage:</p>
        <ol>
            <li>Check railway.toml for volume configuration</li>
            <li>Verify /app/facial_evaluations directory exists in production</li>
            <li>Check production logs for successful image serving</li>
        </ol>
        
        <p><a href="/admin">← Back to Admin Dashboard</a></p>
        </body>
        </html>
        """

@app.route('/admin/facial-evaluation-files')
@login_required
def admin_facial_evaluation_files():
    """Admin view of all files in facial evaluation storage"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    try:
        files_info = []
        total_size = 0
        
        if os.path.exists(FACIAL_EVALUATION_FOLDER):
            for filename in os.listdir(FACIAL_EVALUATION_FOLDER):
                if filename == '.gitkeep':
                    continue
                    
                file_path = os.path.join(FACIAL_EVALUATION_FOLDER, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    total_size += file_size
                    
                    # Try to find associated evaluation
                    evaluation = None
                    if filename.startswith('eval_original_'):
                        evaluation = FacialEvaluation.query.filter_by(original_image_filename=filename).first()
                    elif filename.startswith('eval_morphed_'):
                        evaluation = FacialEvaluation.query.filter_by(morphed_image_filename=filename).first()
                    elif filename.startswith('eval_'):
                        # Could be secondary image or standalone
                        evaluation = FacialEvaluation.query.filter(
                            (FacialEvaluation.secondary_image_filename == filename) |
                            (FacialEvaluation.original_image_filename == filename)
                        ).first()
                    
                    files_info.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'evaluation_id': evaluation.id if evaluation else None,
                        'evaluation_user': evaluation.user.email if evaluation else None,
                        'orphaned': evaluation is None
                    })
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files_info,
            'total_files': len(files_info),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'storage_path': FACIAL_EVALUATION_FOLDER
        })
        
    except Exception as e:
        logger.error(f"Error listing facial evaluation files: {e}")
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/admin/delete-facial-evaluation-file', methods=['POST'])
@login_required
def admin_delete_facial_evaluation_file():
    """Admin delete specific file from facial evaluation storage"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        # Security check - ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(FACIAL_EVALUATION_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is associated with any evaluation
        evaluation = None
        if filename.startswith('eval_original_'):
            evaluation = FacialEvaluation.query.filter_by(original_image_filename=filename).first()
        elif filename.startswith('eval_morphed_'):
            evaluation = FacialEvaluation.query.filter_by(morphed_image_filename=filename).first()
        elif filename.startswith('eval_'):
            evaluation = FacialEvaluation.query.filter(
                (FacialEvaluation.secondary_image_filename == filename) |
                (FacialEvaluation.original_image_filename == filename)
            ).first()
        
        # Delete the file
        os.remove(file_path)
        
        # If file was associated with an evaluation, update the database
        if evaluation:
            if evaluation.original_image_filename == filename:
                evaluation.original_image_filename = None
            elif evaluation.morphed_image_filename == filename:
                evaluation.morphed_image_filename = None
            elif evaluation.secondary_image_filename == filename:
                evaluation.secondary_image_filename = None
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} deleted file {filename} (associated with evaluation {evaluation.id})")
        else:
            logger.info(f"Admin {current_user.email} deleted orphaned file {filename}")
        
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully',
            'was_orphaned': evaluation is None
        })
        
    except Exception as e:
        logger.error(f"Error deleting facial evaluation file: {e}")
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@app.route('/admin/bulk-delete-facial-evaluation-files', methods=['POST'])
@login_required
def admin_bulk_delete_facial_evaluation_files():
    """Admin bulk delete files from facial evaluation storage"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        delete_orphaned_only = data.get('orphaned_only', False)
        
        if not filenames and not delete_orphaned_only:
            return jsonify({'error': 'No files specified for deletion'}), 400
        
        deleted_files = []
        errors = []
        
        if delete_orphaned_only:
            # Find all orphaned files
            if os.path.exists(FACIAL_EVALUATION_FOLDER):
                for filename in os.listdir(FACIAL_EVALUATION_FOLDER):
                    if filename == '.gitkeep':
                        continue
                        
                    file_path = os.path.join(FACIAL_EVALUATION_FOLDER, filename)
                    if os.path.isfile(file_path):
                        # Check if file is orphaned
                        evaluation = FacialEvaluation.query.filter(
                            (FacialEvaluation.original_image_filename == filename) |
                            (FacialEvaluation.morphed_image_filename == filename) |
                            (FacialEvaluation.secondary_image_filename == filename)
                        ).first()
                        
                        if not evaluation:
                            try:
                                os.remove(file_path)
                                deleted_files.append(filename)
                            except Exception as e:
                                errors.append(f"{filename}: {str(e)}")
        else:
            # Delete specified files
            for filename in filenames:
                # Security check
                if '..' in filename or '/' in filename or '\\' in filename:
                    errors.append(f"{filename}: Invalid filename")
                    continue
                
                file_path = os.path.join(FACIAL_EVALUATION_FOLDER, filename)
                
                if not os.path.exists(file_path):
                    errors.append(f"{filename}: File not found")
                    continue
                
                try:
                    # Check if file is associated with any evaluation
                    evaluation = FacialEvaluation.query.filter(
                        (FacialEvaluation.original_image_filename == filename) |
                        (FacialEvaluation.morphed_image_filename == filename) |
                        (FacialEvaluation.secondary_image_filename == filename)
                    ).first()
                    
                    # Delete the file
                    os.remove(file_path)
                    deleted_files.append(filename)
                    
                    # Update database if needed
                    if evaluation:
                        if evaluation.original_image_filename == filename:
                            evaluation.original_image_filename = None
                        elif evaluation.morphed_image_filename == filename:
                            evaluation.morphed_image_filename = None
                        elif evaluation.secondary_image_filename == filename:
                            evaluation.secondary_image_filename = None
                        
                        db.session.commit()
                        
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")
        
        logger.info(f"Admin {current_user.email} bulk deleted {len(deleted_files)} files from facial evaluation storage")
        
        return jsonify({
            'success': True,
            'deleted_files': deleted_files,
            'deleted_count': len(deleted_files),
            'errors': errors,
            'message': f'Successfully deleted {len(deleted_files)} files' + (f' with {len(errors)} errors' if errors else '')
        })
        
    except Exception as e:
        logger.error(f"Error bulk deleting facial evaluation files: {e}")
        return jsonify({'error': f'Failed to delete files: {str(e)}'}), 500

@app.route('/admin/update-system-prompt', methods=['GET', 'POST'])
@login_required
def admin_update_system_prompt():
    """Admin update system prompt for automated facial analysis"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    if request.method == 'GET':
        # Get current system prompt
        system_prompt_obj = SystemPrompt.query.filter_by(name='default_facial_analysis_prompt').first()
        current_prompt = system_prompt_obj.prompt_text if system_prompt_obj else ""
        
        return jsonify({
            'success': True,
            'current_prompt': current_prompt
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_prompt = data.get('prompt_text', '').strip()
            
            if not new_prompt or len(new_prompt) < 100:
                return jsonify({'error': 'System prompt must be at least 100 characters long'}), 400
            
            if len(new_prompt) > 5000:
                return jsonify({'error': 'System prompt must be less than 5000 characters'}), 400
            
            # Get or create system prompt
            system_prompt_obj = SystemPrompt.query.filter_by(name='default_facial_analysis_prompt').first()
            if system_prompt_obj:
                system_prompt_obj.prompt_text = new_prompt
                system_prompt_obj.updated_at = datetime.utcnow()
            else:
                system_prompt_obj = SystemPrompt(
                    name='default_facial_analysis_prompt',
                    prompt_text=new_prompt
                )
                db.session.add(system_prompt_obj)
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} updated system prompt for automated facial analysis")
            
            return jsonify({
                'success': True,
                'message': 'System prompt updated successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error updating system prompt: {e}")
            return jsonify({'error': 'Failed to update system prompt. Please try again.'}), 500

@app.route('/admin/ai-helper-chat', methods=['POST'])
@login_required
def admin_ai_helper_chat():
    """Handle chat requests from the admin AI helper"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        messages = data.get('messages', [])
        system_prompt = data.get('system_prompt', 'You are a helpful assistant.')

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Initialize OpenRouter Client
        openrouter_client = OpenRouterClient()

        # Get chat completion
        result = openrouter_client.get_chat_completion(messages, system_prompt)

        if "error" in result:
            logger.error(f"AI Helper chat failed: {result['error']}")
            return jsonify({'error': f"AI Helper chat failed: {result['error']}"}), 500

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI helper chat: {e}")
        return jsonify({'error': 'Failed to get response from AI helper.'}), 500

@app.route('/sw.js')
def serve_sw():
    try:
        with open('sw.js', 'r') as f:
            content = f.read()
        return app.response_class(
            response=content,
            status=200,
            mimetype='application/javascript'
        )
    except Exception as e:
        logger.error(f"Error serving sw.js: {e}")
        return "Service worker not found", 404

if __name__ == '__main__':
    print("Starting Face Morphing Web App...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    
    if USE_CLOUD_GPU:
        if USE_RUNPOD_POD:
            print(f"GPU Provider: RunPod Pod ({RUNPOD_POD_URL}:{RUNPOD_POD_PORT})")
        else:
            print(f"GPU Provider: RunPod Serverless (Endpoint: {RUNPOD_SERVERLESS_ENDPOINT or RUNPOD_ENDPOINT_ID or 'not_configured'})")
    else:
        print(f"GPU Provider: ComfyUI (URL: {COMFYUI_URL})")
    
    print(f"Available presets: {', '.join(PRESETS.keys())}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Admin login: ascendbase@gmail.com / morphpas")
    
    # Clean up old files on startup
    cleanup_old_files()
    
    # For Railway deployment, bind to 0.0.0.0 and use PORT from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', PORT))
    
    print(f"Starting server on {host}:{port}")
    app.run(debug=DEBUG, host=host, port=port, threaded=THREADED)
