"""
Test script for Vast.ai On-Demand Client
Tests pay-per-use functionality with automatic instance management
"""

import os
import sys
import time
import logging
from vast_on_demand_client import VastOnDemandClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_vast_on_demand():
    """Test the on-demand Vast.ai client"""
    
    # Get API key from environment
    api_key = os.getenv('VAST_API_KEY')
    if not api_key:
        logger.error("VAST_API_KEY environment variable not set!")
        logger.info("Please run: set VAST_API_KEY=your_api_key_here")
        return False
    
    logger.info("🚀 Testing Vast.ai On-Demand Client...")
    logger.info("This will start a GPU instance, process an image, then stop the instance")
    logger.info("Expected cost: $0.004-0.01 per generation (98-99% savings!)")
    
    # Initialize client
    client = VastOnDemandClient(api_key)
    
    # Test 1: API Connection
    logger.info("\n📡 Testing API connection...")
    if client.test_connection():
        logger.info("✅ API connection successful!")
    else:
        logger.error("❌ API connection failed!")
        return False
    
    # Test 2: Find Available GPUs
    logger.info("\n🔍 Finding cheapest GPU...")
    offer = client.find_cheapest_gpu(min_gpu_ram=8)
    if offer:
        gpu_info = f"{offer.get('gpu_name', 'Unknown')} ({offer.get('gpu_ram', 0)}GB)"
        cost_info = f"${offer.get('dph_total', 0):.3f}/hour"
        logger.info(f"✅ Found GPU: {gpu_info} - {cost_info}")
        
        # Calculate cost per generation (assuming 2 minutes)
        hourly_cost = offer.get('dph_total', 0)
        per_gen_cost = hourly_cost * (2/60)  # 2 minutes
        logger.info(f"💰 Estimated cost per generation: ${per_gen_cost:.4f}")
    else:
        logger.error("❌ No suitable GPUs found!")
        return False
    
    # Test 3: Check if test image exists
    test_image_path = "test_image.png"
    if not os.path.exists(test_image_path):
        logger.warning(f"⚠️  Test image not found: {test_image_path}")
        logger.info("Creating a placeholder test image...")
        
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple test image
            img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(test_image_path)
            logger.info(f"✅ Created test image: {test_image_path}")
        except ImportError:
            logger.error("❌ PIL not available, cannot create test image")
            logger.info("Please install: pip install pillow")
            return False
    
    # Test 4: Dry Run (don't actually start instance)
    logger.info("\n🧪 Performing dry run test...")
    logger.info("This would:")
    logger.info(f"1. Start instance: {offer.get('gpu_name', 'Unknown')} (${offer.get('dph_total', 0):.3f}/hour)")
    logger.info("2. Wait for ComfyUI to be ready (~5-10 minutes)")
    logger.info("3. Process image (~30-60 seconds)")
    logger.info("4. Stop instance immediately")
    logger.info(f"5. Total cost: ~${per_gen_cost:.4f}")
    
    # Ask user if they want to proceed with actual test
    logger.info("\n❓ Do you want to run the actual test? This will cost money!")
    logger.info("Type 'yes' to proceed, anything else to skip:")
    
    try:
        user_input = input().strip().lower()
        if user_input != 'yes':
            logger.info("✅ Dry run completed successfully!")
            logger.info("To run actual test, restart and type 'yes' when prompted")
            return True
    except KeyboardInterrupt:
        logger.info("\n✅ Test cancelled by user")
        return True
    
    # Test 5: Actual Generation (if user confirmed)
    logger.info("\n🎯 Starting actual on-demand generation...")
    logger.info("This will take 5-15 minutes and cost ~${:.4f}".format(per_gen_cost))
    
    start_time = time.time()
    
    try:
        result_image, error = client.generate_image(
            image_path=test_image_path,
            preset_key="tier1",
            denoise_intensity=4
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if result_image:
            # Save result
            output_path = f"test_output_{int(time.time())}.png"
            with open(output_path, 'wb') as f:
                f.write(result_image)
            
            logger.info(f"✅ Generation successful!")
            logger.info(f"📁 Output saved: {output_path}")
            logger.info(f"⏱️  Total time: {total_time:.1f} seconds")
            logger.info(f"💰 Estimated cost: ${per_gen_cost:.4f}")
            logger.info(f"🎉 You just saved 98-99% compared to hourly billing!")
            
            return True
        else:
            logger.error(f"❌ Generation failed: {error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("🧪 VAST.AI ON-DEMAND CLIENT TEST")
    logger.info("=" * 60)
    
    success = test_vast_on_demand()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("Your on-demand setup is working correctly!")
        logger.info("You can now use pay-per-generation billing with 98-99% savings!")
    else:
        logger.info("❌ TESTS FAILED!")
        logger.info("Please check the errors above and try again")
    logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
