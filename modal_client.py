"""
Modal.com client for face morphing app integration
Provides fast, cost-effective GPU processing with custom models
"""

import base64
import io
import os
import time
import logging
from PIL import Image
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ModalMorphClient:
    """Client for Modal.com face morphing service"""
    
    def __init__(self):
        """Initialize Modal client"""
        self.app_name = "face-morph-simple"
        self.function_name = "generate_face_morph"
        self.modal = None
        self.app = None
        self.token_configured = False
        
        # Import Modal here to avoid issues if not installed
        try:
            import modal
            self.modal = modal
            
            # Check if token is configured
            try:
                # Try to get current token info
                modal.config._get_token_flow()
                self.token_configured = True
                logger.info("Modal token found")
            except Exception:
                self.token_configured = False
                logger.warning("Modal token not configured. Please run 'modal token new' to set up authentication.")
            
            # Only try to lookup function if token is configured
            if self.token_configured:
                try:
                    self.generate_func = modal.Function.lookup(self.app_name, self.function_name)
                    logger.info("Modal client initialized successfully")
                except Exception as e:
                    logger.warning(f"Modal function '{self.function_name}' not found. Please deploy it first: {e}")
                    self.generate_func = None
            else:
                logger.info("Modal client initialized but not authenticated")
                self.generate_func = None
                
        except ImportError:
            logger.error("Modal not installed. Run: pip install modal")
            self.modal = None
            self.app = None
        except Exception as e:
            logger.error(f"Failed to initialize Modal client: {e}")
            self.modal = None
            self.app = None
    
    def test_connection(self) -> bool:
        """Test connection to Modal service"""
        try:
            if not self.modal or not self.generate_func:
                return False
            
            # Try to get the test function
            test_func = modal.Function.lookup(self.app_name, "test_setup")
            if test_func:
                result = test_func.remote()
                logger.info(f"Modal connection test: {result}")
                return True
            return False
        except Exception as e:
            logger.error(f"Modal connection test failed: {e}")
            return False
    
    def generate_image(self, image_path: str, preset_key: str, denoise_intensity: int = 4) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Generate face morph using Modal.com
        
        Args:
            image_path: Path to input image
            preset_key: Preset key (tier1, tier2, chad)
            denoise_intensity: Intensity level (1-10, maps to 0.10-0.25 denoise)
        
        Returns:
            tuple: (image_bytes, error_message)
        """
        try:
            if not self.modal or not self.generate_func:
                return None, "Modal client not initialized"
            
            logger.info(f"Starting Modal generation: {preset_key}, intensity: {denoise_intensity}")
            
            # Convert intensity to denoise strength
            denoise_strength = 0.10 + (denoise_intensity - 1) * 0.015  # Maps 1-10 to 0.10-0.25
            denoise_strength = max(0.10, min(0.25, denoise_strength))
            
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_b64 = base64.b64encode(image_data).decode()
            
            # Call Modal function
            start_time = time.time()
            result_b64, error = self.generate_func.remote(
                image_b64=image_b64,
                preset_key=preset_key,
                denoise_strength=denoise_strength
            )
            
            generation_time = time.time() - start_time
            logger.info(f"Modal generation completed in {generation_time:.1f}s")
            
            if error:
                logger.error(f"Modal generation error: {error}")
                return None, error
            
            if result_b64:
                # Decode result image
                result_bytes = base64.b64decode(result_b64)
                logger.info(f"Modal generation successful: {len(result_bytes)} bytes")
                return result_bytes, None
            else:
                return None, "No result image returned"
                
        except Exception as e:
            logger.error(f"Modal generation error: {e}")
            return None, str(e)
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get job status (Modal completes synchronously, so always return COMPLETED)
        
        Args:
            job_id: Job ID (not used for Modal)
        
        Returns:
            str: Job status
        """
        # Modal functions are synchronous, so if we get here, it's completed
        return "COMPLETED"
    
    def get_job_output(self, job_id: str) -> Optional[bytes]:
        """
        Get job output (Modal returns output directly, so this is not used)
        
        Args:
            job_id: Job ID (not used for Modal)
        
        Returns:
            bytes: Output image data (None for Modal as it returns directly)
        """
        # Modal returns output directly in generate_image, so this is not used
        return None
    
    def get_cost_estimate(self, preset_key: str) -> dict:
        """
        Get cost estimate for generation
        
        Args:
            preset_key: Preset key
        
        Returns:
            dict: Cost information
        """
        # Modal T4 pricing: ~$0.0004/second
        # Estimated generation time: 60-120 seconds
        estimated_time = 90  # seconds
        cost_per_second = 0.0004
        estimated_cost = estimated_time * cost_per_second
        
        return {
            'provider': 'Modal.com',
            'gpu_type': 'T4',
            'estimated_time_seconds': estimated_time,
            'estimated_cost_usd': estimated_cost,
            'cost_per_second': cost_per_second,
            'preset': preset_key
        }

# Compatibility functions for existing code
def create_modal_client() -> ModalMorphClient:
    """Create Modal client instance"""
    return ModalMorphClient()

def test_modal_connection() -> bool:
    """Test Modal connection"""
    client = create_modal_client()
    return client.test_connection()

# Example usage
if __name__ == "__main__":
    # Test the client
    client = ModalMorphClient()
    
    print("🧪 Testing Modal client...")
    
    # Test connection
    if client.test_connection():
        print("✅ Modal connection successful")
    else:
        print("❌ Modal connection failed")
    
    # Test cost estimate
    cost_info = client.get_cost_estimate("tier1")
    print(f"💰 Cost estimate: ${cost_info['estimated_cost_usd']:.4f}")
    
    # Test generation (if test image exists)
    test_image = "test_image.png"
    if os.path.exists(test_image):
        print(f"🎨 Testing generation with {test_image}...")
        result_bytes, error = client.generate_image(test_image, "tier1", 4)
        
        if error:
            print(f"❌ Generation failed: {error}")
        elif result_bytes:
            print(f"✅ Generation successful: {len(result_bytes)} bytes")
            
            # Save result
            with open("modal_test_result.png", "wb") as f:
                f.write(result_bytes)
            print("💾 Result saved as modal_test_result.png")
        else:
            print("❌ No result returned")
    else:
        print(f"⚠️ Test image {test_image} not found")
