"""
Debug script to identify why generation isn't working
"""

import os
import sys
import logging
from config import *

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_configuration():
    """Debug the current configuration"""
    print("=" * 60)
    print("🔍 DEBUGGING GENERATION ISSUE")
    print("=" * 60)
    
    print("\n📋 Current Configuration:")
    print(f"USE_CLOUD_GPU: {USE_CLOUD_GPU}")
    print(f"VAST_ON_DEMAND_MODE: {VAST_ON_DEMAND_MODE}")
    print(f"VAST_API_KEY: {VAST_API_KEY[:20]}..." if VAST_API_KEY else "VAST_API_KEY: Not set")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    
    print("\n🔧 GPU Client Initialization Test:")
    
    try:
        if USE_CLOUD_GPU:
            if VAST_ON_DEMAND_MODE:
                print("✅ Should use Vast.ai On-Demand client")
                from vast_on_demand_client import VastOnDemandClient
                client = VastOnDemandClient(VAST_API_KEY)
                print("✅ VastOnDemandClient imported successfully")
                
                # Test API connection
                print("🔗 Testing API connection...")
                if client.test_connection():
                    print("✅ API connection successful!")
                else:
                    print("❌ API connection failed!")
                    return False
                    
            else:
                print("✅ Should use regular Vast.ai client")
                from vast_client import VastMorphClient
                client = VastMorphClient()
                print("✅ VastMorphClient imported successfully")
        else:
            print("✅ Should use local ComfyUI client")
            from comfyui_client import ComfyUIClient
            client = ComfyUIClient(COMFYUI_URL)
            print("✅ ComfyUIClient imported successfully")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Client initialization error: {e}")
        return False
    
    print("\n🧪 Testing Image Generation Flow:")
    
    # Check if test image exists
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
        print("Creating a test image...")
        try:
            from PIL import Image
            import numpy as np
            img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(test_image)
            print(f"✅ Created test image: {test_image}")
        except ImportError:
            print("❌ PIL not available, cannot create test image")
            return False
    else:
        print(f"✅ Test image found: {test_image}")
    
    # Test generation (dry run)
    print("\n🎯 Testing Generation (Dry Run):")
    try:
        if USE_CLOUD_GPU and VAST_ON_DEMAND_MODE:
            print("Testing Vast.ai On-Demand generation...")
            
            # Test finding GPU
            offer = client.find_cheapest_gpu(min_gpu_ram=8)
            if offer:
                gpu_info = f"{offer.get('gpu_name', 'Unknown')} ({offer.get('gpu_ram', 0)}GB)"
                cost_info = f"${offer.get('dph_total', 0):.3f}/hour"
                print(f"✅ Found GPU: {gpu_info} - {cost_info}")
                
                # Calculate cost per generation
                hourly_cost = offer.get('dph_total', 0)
                per_gen_cost = hourly_cost * (2/60)  # 2 minutes
                print(f"💰 Estimated cost per generation: ${per_gen_cost:.4f}")
                
                print("✅ Dry run successful - ready for actual generation!")
                return True
            else:
                print("❌ No suitable GPUs found")
                return False
        else:
            print("✅ Configuration test passed")
            return True
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_app_imports():
    """Debug app.py imports"""
    print("\n📦 Testing App Imports:")
    
    try:
        # Test imports that app.py uses
        from vast_client import VastMorphClient
        print("✅ vast_client imported successfully")
    except ImportError as e:
        print(f"❌ vast_client import failed: {e}")
    
    try:
        from vast_on_demand_client import VastOnDemandClient
        print("✅ vast_on_demand_client imported successfully")
    except ImportError as e:
        print(f"❌ vast_on_demand_client import failed: {e}")
    
    try:
        from comfyui_client import ComfyUIClient
        print("✅ comfyui_client imported successfully")
    except ImportError as e:
        print(f"❌ comfyui_client import failed: {e}")

def check_environment_variables():
    """Check environment variables"""
    print("\n🌍 Environment Variables:")
    
    env_vars = [
        'VAST_API_KEY',
        'VAST_ON_DEMAND_MODE', 
        'USE_CLOUD_GPU',
        'VAST_AUTO_STOP_INSTANCES',
        'VAST_MAX_INSTANCE_LIFETIME'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var:
                print(f"✅ {var}: {value[:20]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (using default)")

def main():
    """Main debug function"""
    print("Starting generation debug...")
    
    check_environment_variables()
    debug_app_imports()
    
    success = debug_configuration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DEBUG PASSED!")
        print("Configuration looks good. Generation should work.")
        print("\nIf generation still fails, check:")
        print("1. Network connectivity")
        print("2. Vast.ai account balance")
        print("3. Available GPU instances")
    else:
        print("❌ DEBUG FAILED!")
        print("Found issues that need to be fixed.")
        print("\nCommon fixes:")
        print("1. Check VAST_API_KEY is correct")
        print("2. Ensure internet connection")
        print("3. Verify Vast.ai account is active")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
