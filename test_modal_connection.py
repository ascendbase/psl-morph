"""
Complete Modal.com connection and functionality test
"""

import os
import sys
import base64
import io
from PIL import Image
import requests
import time

def test_modal_token():
    """Test if Modal token is configured"""
    print("🔍 Testing Modal token configuration...")
    
    try:
        import modal
        
        # Check if token exists
        token = os.getenv('MODAL_TOKEN')
        if token:
            print(f"✅ Modal token found: {token[:10]}...")
        else:
            print("❌ Modal token not found in environment")
            return False
            
        # Try to authenticate
        try:
            client = modal.Client()
            print("✅ Modal client created successfully")
            return True
        except Exception as e:
            print(f"❌ Modal authentication failed: {e}")
            return False
            
    except ImportError:
        print("❌ Modal package not installed")
        return False

def test_modal_app_deployment():
    """Test if Modal app is deployed"""
    print("\n🔍 Testing Modal app deployment...")
    
    try:
        import modal
        
        # Check if app exists
        try:
            app = modal.App.lookup("face-morph-simple")
            print("✅ Modal app 'face-morph-simple' found")
            
            # List functions
            functions = list(app.registered_functions.keys())
            print(f"✅ Available functions: {functions}")
            
            if 'generate_face_morph' in str(functions):
                print("✅ generate_face_morph function found")
                return True
            else:
                print("❌ generate_face_morph function not found")
                return False
                
        except Exception as e:
            print(f"❌ Modal app not found or not accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Modal app: {e}")
        return False

def test_modal_function_call():
    """Test calling Modal function directly"""
    print("\n🔍 Testing Modal function call...")
    
    try:
        import modal
        
        # Create test image
        test_image = Image.new('RGB', (512, 512), color='red')
        buffered = io.BytesIO()
        test_image.save(buffered, format="PNG")
        test_image_b64 = base64.b64encode(buffered.getvalue()).decode()
        
        print("✅ Test image created")
        
        # Get the app and function
        app = modal.App.lookup("face-morph-simple")
        generate_face_morph = app.registered_functions['generate_face_morph']
        
        print("🚀 Calling Modal function...")
        start_time = time.time()
        
        # Call the function
        result = generate_face_morph.remote(
            image_b64=test_image_b64,
            preset_key="tier1",
            denoise_strength=0.15
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result and len(result) == 2:
            result_image_b64, error_message = result
            
            if result_image_b64 and not error_message:
                print(f"✅ Modal function call successful! Duration: {duration:.2f}s")
                print(f"✅ Result image size: {len(result_image_b64)} characters")
                return True
            else:
                print(f"❌ Modal function returned error: {error_message}")
                return False
        else:
            print(f"❌ Modal function returned unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling Modal function: {e}")
        return False

def test_local_modal_client():
    """Test local Modal client integration"""
    print("\n🔍 Testing local Modal client...")
    
    try:
        # Import local modal client
        sys.path.append('.')
        from modal_client import ModalMorphClient
        
        client = ModalMorphClient()
        print("✅ Local Modal client created")
        
        # Test authentication
        if client.token_configured:
            print("✅ Modal client authenticated")
        else:
            print("❌ Modal client not authenticated")
            return False
            
        # Test app deployment check
        if client.app is not None:
            print("✅ Modal app deployment verified")
        else:
            print("❌ Modal app not deployed")
            return False
            
        # Test image generation with test image file
        test_image_path = "test_image.png"
        
        # Create test image file
        test_image = Image.new('RGB', (512, 512), color='blue')
        test_image.save(test_image_path)
        print("✅ Test image file created")
        
        print("🚀 Testing image generation through local client...")
        start_time = time.time()
        
        result_bytes, error = client.generate_image(
            image_path=test_image_path,
            preset_key="tier1",
            denoise_intensity=4
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Clean up test image
        try:
            os.remove(test_image_path)
        except:
            pass
        
        if result_bytes and not error:
            print(f"✅ Local Modal client generation successful! Duration: {duration:.2f}s")
            print(f"✅ Result size: {len(result_bytes)} bytes")
            return True
        else:
            print(f"❌ Local Modal client generation failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing local Modal client: {e}")
        return False

def test_app_integration():
    """Test app integration with Modal"""
    print("\n🔍 Testing app integration with Modal...")
    
    try:
        # Import app modules
        sys.path.append('.')
        import config
        
        # Check configuration
        if hasattr(config, 'USE_MODAL') and config.USE_MODAL:
            print("✅ USE_MODAL is enabled in config")
        else:
            print("❌ USE_MODAL is not enabled in config")
            return False
            
        if hasattr(config, 'USE_CLOUD_GPU') and not config.USE_CLOUD_GPU:
            print("✅ USE_CLOUD_GPU is disabled (Modal priority)")
        else:
            print("⚠️ USE_CLOUD_GPU is still enabled (may interfere)")
            
        # Test app health endpoint simulation
        print("🔍 Testing app health check logic...")
        
        # Simulate what the health endpoint would return
        gpu_provider = "modal.com" if config.USE_MODAL else "other"
        print(f"✅ GPU provider would be: {gpu_provider}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app integration: {e}")
        return False

def run_all_tests():
    """Run all Modal connection tests"""
    print("🚀 MODAL.COM CONNECTION TESTS")
    print("=" * 50)
    
    tests = [
        ("Modal Token", test_modal_token),
        ("Modal App Deployment", test_modal_app_deployment),
        ("Modal Function Call", test_modal_function_call),
        ("Local Modal Client", test_local_modal_client),
        ("App Integration", test_app_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Modal.com is ready to use!")
        print("💰 You can now enjoy 95% cost savings vs RunPod!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
