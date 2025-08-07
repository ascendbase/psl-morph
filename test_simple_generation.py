"""
Simple test of RunPod generation without database
"""

import os
from dotenv import load_dotenv
from runpod_client import RunPodClient

def test_simple_generation():
    """Test RunPod generation directly"""
    
    print("🎯 SIMPLE RUNPOD GENERATION TEST")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Get credentials
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"Endpoint ID: {endpoint_id if endpoint_id else '❌ Missing'}")
    
    if not api_key or not endpoint_id:
        print("❌ Missing credentials!")
        return
    
    # Initialize client
    try:
        client = RunPodClient(api_key, endpoint_id)
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Client failed: {e}")
        return
    
    # Test connection
    try:
        connected = client.test_connection()
        print(f"Connection: {'✅ Success' if connected else '❌ Failed'}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Test image
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    print(f"✅ Test image found: {test_image}")
    
    # Test generation with HTN preset
    print(f"\n🚀 Testing HTN generation...")
    try:
        result, error = client.generate_image(
            image_path=test_image,
            preset_key='HTN',
            denoise_intensity=4
        )
        
        if error:
            print(f"❌ Generation failed: {error}")
            return
        
        print(f"✅ Generation submitted successfully!")
        print(f"Job ID: {result}")
        print(f"This proves your RunPod serverless is working!")
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_generation()
