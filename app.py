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
from models import db, User, Generation, Transaction, init_db
from auth import auth_bp, init_login_manager
from payments import payments_bp
from runpod_client import RunPodClient

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

# Initialize database and authentication
init_db(app)
login_manager = init_login_manager(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(payments_bp)

# Initialize GPU client
gpu_client = None
if USE_CLOUD_GPU:
    if USE_RUNPOD_POD:
        # Use RunPod pod (direct connection to ComfyUI)
        from runpod_pod_client import RunPodPodClient
        gpu_client = RunPodPodClient(
            pod_url=RUNPOD_POD_URL,
            pod_port=RUNPOD_POD_PORT
        )
        logger.info(f"Initialized RunPod Pod client: {RUNPOD_POD_URL}:{RUNPOD_POD_PORT}")
    else:
        # Use RunPod serverless endpoint
        gpu_client = RunPodClient(
            api_key=RUNPOD_API_KEY,
            endpoint_id=RUNPOD_ENDPOINT_ID
        )
        logger.info(f"Initialized RunPod serverless client with endpoint: {RUNPOD_ENDPOINT_ID}")
else:
    from comfyui_client import ComfyUIClient
    gpu_client = ComfyUIClient(COMFYUI_URL)
    logger.info(f"Initialized ComfyUI client: {COMFYUI_URL}")

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(WORKFLOW_FOLDER, exist_ok=True)

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
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate denoise value
        try:
            denoise_value = float(denoise_str)
            if denoise_value < 0.10 or denoise_value > 0.25:
                return jsonify({'error': 'Invalid denoise value. Must be between 0.10 and 0.25'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid denoise value format'}), 400
        
        # Check if user can generate
        can_free = current_user.can_generate_free()
        can_paid = current_user.can_generate_paid()
        
        if not can_free and not can_paid:
            return jsonify({
                'error': 'No credits available. Purchase credits or wait until tomorrow for your free generation.',
                'need_credits': True
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
        
        data = request.get_json()
        filename = data.get('filename')
        denoise_value = data.get('denoise', 0.10)
        use_free_credit = data.get('use_free_credit', True)
        
        if not filename or not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            return jsonify({'error': 'File not found'}), 404
        
        # Validate denoise value
        if not isinstance(denoise_value, (int, float)) or denoise_value < 0.10 or denoise_value > 0.25:
            return jsonify({'error': 'Invalid denoise value. Must be between 0.10 and 0.25'}), 400
        
        # Check and deduct credits
        used_free = False
        used_paid = False
        
        if use_free_credit and current_user.can_generate_free():
            current_user.use_free_generation()
            used_free = True
        elif current_user.can_generate_paid():
            if current_user.use_paid_credit():
                used_paid = True
            else:
                return jsonify({'error': 'Failed to deduct credit'}), 402
        else:
            return jsonify({
                'error': 'No credits available. Purchase credits or wait until tomorrow for your free generation.',
                'need_credits': True
            }), 402
        
        # Determine tier name for logging
        tier_name = 'custom'
        if denoise_value == 0.10:
            tier_name = '+1_Tier'
        elif denoise_value == 0.15:
            tier_name = '+2_Tier'
        elif denoise_value == 0.25:
            tier_name = 'Chad'
        
        # Create generation record
        generation = Generation(
            user_id=current_user.id,
            preset=tier_name,  # Store tier name for compatibility
            workflow_type='runpod' if USE_CLOUD_GPU else CURRENT_WORKFLOW,
            input_filename=filename,
            used_free_credit=used_free,
            used_paid_credit=used_paid,
            status='pending'
        )
        
        db.session.add(generation)
        db.session.commit()
        
        if USE_CLOUD_GPU:
            # Use RunPod for processing
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # Start RunPod generation
                job_id = gpu_client.generate_image(
                    image_path=file_path,
                    denoise_strength=denoise_value,
                    preset_name=tier_name
                )
                
                if not job_id:
                    generation.status = 'failed'
                    generation.error_message = 'Failed to start RunPod generation'
                    db.session.commit()
                    return jsonify({'error': 'Failed to start generation'}), 500
                
                # Update generation with job ID
                generation.prompt_id = job_id
                generation.status = 'processing'
                generation.started_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"RunPod processing started for {current_user.email}: {job_id} (free: {used_free}, paid: {used_paid})")
                
                return jsonify({
                    'success': True,
                    'prompt_id': job_id,
                    'generation_id': generation.id,
                    'denoise': denoise_value,
                    'tier_name': tier_name,
                    'used_free_credit': used_free,
                    'used_paid_credit': used_paid,
                    'remaining_credits': current_user.credits,
                    'message': f'Processing started with {tier_name.replace("_", " ")} tier on RTX 5090...'
                })
                
            except Exception as e:
                generation.status = 'failed'
                generation.error_message = str(e)
                db.session.commit()
                logger.error(f"RunPod processing error: {e}")
                return jsonify({'error': f'RunPod processing failed: {str(e)}'}), 500
        
        else:
            # Use ComfyUI for processing
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # Start ComfyUI generation using the client
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
                
                # Update generation with prompt ID
                generation.prompt_id = prompt_id
                generation.status = 'processing'
                generation.started_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"ComfyUI processing started for {current_user.email}: {prompt_id} (free: {used_free}, paid: {used_paid})")
                
                return jsonify({
                    'success': True,
                    'prompt_id': prompt_id,
                    'generation_id': generation.id,
                    'denoise': denoise_value,
                    'tier_name': tier_name,
                    'used_free_credit': used_free,
                    'used_paid_credit': used_paid,
                    'remaining_credits': current_user.credits,
                    'message': f'Processing started with {tier_name.replace("_", " ")} tier on RTX 5090...'
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
        if USE_CLOUD_GPU:
            # Check RunPod job status
            status = gpu_client.get_job_status(prompt_id)
            
            if status == 'COMPLETED':
                return jsonify({
                    'complete': True,
                    'message': 'Processing complete!'
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
        else:
            # Check ComfyUI workflow status
            status = gpu_client.get_job_status(prompt_id)
            
            if status == 'COMPLETED':
                return jsonify({
                    'complete': True,
                    'message': 'Processing complete!'
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if USE_CLOUD_GPU:
            # Check RunPod connection
            gpu_status = "connected" if gpu_client.test_connection() else "disconnected"
            if USE_RUNPOD_POD:
                gpu_type = "runpod_pod"
                gpu_info = f"Pod: {RUNPOD_POD_URL}:{RUNPOD_POD_PORT}"
            else:
                gpu_type = "runpod_serverless"
                gpu_info = f"Endpoint: {RUNPOD_ENDPOINT_ID}"
        else:
            # Check ComfyUI connection
            response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
            gpu_status = "connected" if response.status_code == 200 else "disconnected"
            gpu_type = "comfyui"
            gpu_info = f"Local: {COMFYUI_URL}"
    except:
        gpu_status = "disconnected"
        if USE_CLOUD_GPU:
            gpu_type = "runpod_pod" if USE_RUNPOD_POD else "runpod_serverless"
            gpu_info = f"Pod: {RUNPOD_POD_URL}" if USE_RUNPOD_POD else f"Endpoint: {RUNPOD_ENDPOINT_ID}"
        else:
            gpu_type = "comfyui"
            gpu_info = f"Local: {COMFYUI_URL}"
    
    return jsonify({
        'status': 'healthy',
        'gpu_type': gpu_type,
        'gpu_status': gpu_status,
        'gpu_info': gpu_info,
        'presets': list(PRESETS.keys()),
        'cloud_gpu_enabled': USE_CLOUD_GPU,
        'runpod_pod_enabled': USE_RUNPOD_POD
    })

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
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         users=users,
                         transactions=transactions,
                         generations=generations)

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

if __name__ == '__main__':
    print("Starting Face Morphing Web App...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    
    if USE_CLOUD_GPU:
        if USE_RUNPOD_POD:
            print(f"GPU Provider: RunPod Pod ({RUNPOD_POD_URL}:{RUNPOD_POD_PORT})")
        else:
            print(f"GPU Provider: RunPod Serverless (Endpoint: {RUNPOD_ENDPOINT_ID})")
    else:
        print(f"GPU Provider: ComfyUI (URL: {COMFYUI_URL})")
    
    print(f"Available presets: {', '.join(PRESETS.keys())}")
    print(f"Open http://{HOST}:{PORT} in your browser")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Admin login: ascendbase@gmail.com / morphpas")
    
    # Clean up old files on startup
    cleanup_old_files()
    
    app.run(debug=DEBUG, host=HOST, port=PORT, threaded=THREADED)