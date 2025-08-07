"""
Test the web app generation directly
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Generation
from runpod_client import RunPodClient

def test_web_app_generation():
    """Test generation through the web app logic"""
    
    print("🌐 TESTING WEB APP GENERATION")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Test with app context
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Create test user if doesn't exist
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                credits=100
            )
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
            print("✅ Created test user")
        else:
            print("✅ Test user exists")
        
        # Test the generation logic from app.py
        print(f"\n🎨 Testing generation logic...")
        
        # Simulate the app's generation process
        tier_name = "HTN"
        denoise_value = 0.10
        
        # Map denoise value to preset (from app.py logic)
        if denoise_value <= 0.10:
            preset_key = 'HTN'
            denoise_intensity = 4
        elif denoise_value <= 0.15:
            preset_key = 'Chadlite'
            denoise_intensity = 6
        else:
            preset_key = 'Chad'
            denoise_intensity = 8
        
        print(f"Tier: {tier_name}")
        print(f"Denoise Value: {denoise_value}")
        print(f"Mapped to Preset: {preset_key}")
        print(f"Denoise Intensity: {denoise_intensity}")
        
        # Test image path
        test_image_path = "test_image.png"
        if not os.path.exists(test_image_path):
            print(f"❌ Test image not found: {test_image_path}")
            return
        
        # Initialize GPU client (same as app.py)
        try:
            from config import Config
            gpu_client = RunPodClient(
                Config.RUNPOD_API_KEY,
                Config.RUNPOD_ENDPOINT_ID
            )
            print("✅ GPU client initialized")
        except Exception as e:
            print(f"❌ GPU client failed: {e}")
            return
        
        # Test generation (same parameters as app.py)
        print(f"\n🚀 Starting generation...")
        try:
            result, error = gpu_client.generate_image(
                image_path=test_image_path,
                preset_key=preset_key,
                denoise_intensity=denoise_intensity
            )
            
            if error:
                print(f"❌ Generation failed: {error}")
                return
            
            print(f"✅ Generation request successful!")
            print(f"Result type: {type(result)}")
            
            if isinstance(result, str) and not result.startswith('data:'):
                print(f"Job ID: {result}")
                print(f"This matches the web app flow - job submitted successfully!")
            else:
                print(f"Direct result received")
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_web_app_generation()
