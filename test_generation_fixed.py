"""
Test the fixed generation system
"""

import os
import sys
import time
from config import *

def test_generation():
    """Test the generation system"""
    print("🧪 Testing Fixed Generation System")
    print("=" * 50)
    
    # Test configuration
    print(f"✅ USE_CLOUD_GPU: {USE_CLOUD_GPU}")
    print(f"✅ VAST_ON_DEMAND_MODE: {VAST_ON_DEMAND_MODE}")
    print(f"✅ VAST_API_KEY: {'Set' if VAST_API_KEY else 'Not set'}")
    
    # Initialize client
    try:
        if USE_CLOUD_GPU and VAST_ON_DEMAND_MODE:
            from vast_on_demand_client import VastOnDemandClient
            client = VastOnDemandClient(VAST_API_KEY)
            print("✅ VastOnDemandClient initialized")
        else:
            print("❌ Not using Vast.ai On-Demand mode")
            return False
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test API connection
    print("\n🔗 Testing API Connection...")
    try:
        if client.test_connection():
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False
    
    # Test finding GPU
    print("\n🔍 Finding Available GPU...")
    try:
        offer = client.find_cheapest_gpu(min_gpu_ram=8)
        if offer:
            gpu_info = f"{offer.get('gpu_name', 'Unknown')} ({offer.get('gpu_ram', 0)}GB)"
            cost_info = f"${offer.get('dph_total', 0):.3f}/hour"
            print(f"✅ Found GPU: {gpu_info} - {cost_info}")
            
            # Calculate cost per generation
            hourly_cost = offer.get('dph_total', 0)
            per_gen_cost = hourly_cost * (2/60)  # 2 minutes
            print(f"💰 Cost per generation: ${per_gen_cost:.4f}")
        else:
            print("❌ No suitable GPUs found")
            return False
    except Exception as e:
        print(f"❌ GPU search error: {e}")
        return False
    
    # Test image generation (dry run)
    print("\n🎨 Testing Image Generation (Dry Run)...")
    
    # Check if test image exists
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
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
    
    # Test actual generation
    print("\n🚀 Testing Actual Generation...")
    try:
        print("Starting generation with tier1 preset...")
        result_image, error = client.generate_image(
            image_path=test_image,
            preset_key='tier1',
            denoise_intensity=4
        )
        
        if error:
            print(f"❌ Generation failed: {error}")
            return False
        
        if result_image:
            # Save result
            result_path = f"test_result_{int(time.time())}.png"
            with open(result_path, 'wb') as f:
                f.write(result_image)
            print(f"✅ Generation successful! Result saved: {result_path}")
            print(f"📁 Result size: {len(result_image)} bytes")
            return True
        else:
            print("❌ No result image returned")
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Starting generation test...")
    
    success = test_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Generation system is working correctly!")
        print("\n💡 Next steps:")
        print("1. Deploy to Railway with environment variables")
        print("2. Test through the web interface")
        print("3. Start saving 98% on GPU costs!")
    else:
        print("❌ TESTS FAILED!")
        print("Check the errors above and fix them.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
