#!/usr/bin/env python3
"""
Complete Integration Test for Railway + Local ComfyUI
Tests the entire flow from tunnel registration to image generation
"""

import requests
import json
import time
import os
import sys

# Test configuration
RAILWAY_URL = "https://psl-morph-production.up.railway.app"  # Replace with your Railway URL
TUNNEL_SECRET = "morphpas"  # Default secret
TEST_TUNNEL_URL = "https://keeping-za-volume-enclosed.trycloudflare.com"  # Replace with your tunnel URL

def test_tunnel_registration():
    """Test tunnel registration endpoint"""
    print("🔧 Testing tunnel registration...")
    
    headers = {
        'X-TUNNEL-SECRET': TUNNEL_SECRET,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'url': TEST_TUNNEL_URL
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/register-tunnel",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tunnel registration successful: {result}")
            return True
        else:
            print(f"❌ Tunnel registration failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Tunnel registration error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint to verify tunnel is being used"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful:")
            print(f"   GPU Type: {data.get('gpu_type')}")
            print(f"   GPU Status: {data.get('gpu_status')}")
            print(f"   GPU Info: {data.get('gpu_info')}")
            print(f"   Local ComfyUI Enabled: {data.get('local_comfyui_enabled')}")
            
            # Check if it's using local ComfyUI
            if data.get('gpu_type') == 'local_comfyui':
                print("✅ Railway is configured to use Local ComfyUI")
                return True
            else:
                print("⚠️ Railway is not using Local ComfyUI")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_gpu_status():
    """Test GPU status endpoint"""
    print("🎮 Testing GPU status...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/gpu-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GPU status check successful:")
            print(f"   Available: {data.get('available')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   GPU Type: {data.get('gpu_type')}")
            print(f"   URL: {data.get('url')}")
            
            # Check if GPU is available
            if data.get('available') and data.get('gpu_type') == 'local_comfyui':
                print("✅ Local ComfyUI GPU is available")
                return True
            else:
                print("⚠️ Local ComfyUI GPU is not available")
                return False
        else:
            print(f"❌ GPU status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GPU status error: {e}")
        return False

def test_direct_comfyui_connection():
    """Test direct connection to ComfyUI through tunnel"""
    print("🔗 Testing direct ComfyUI connection...")
    
    try:
        response = requests.get(f"{TEST_TUNNEL_URL}/system_stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct ComfyUI connection successful:")
            print(f"   ComfyUI Version: {data.get('system', {}).get('comfyui_version', 'unknown')}")
            print(f"   Devices: {len(data.get('devices', []))} GPU(s)")
            return True
        else:
            print(f"❌ Direct ComfyUI connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct ComfyUI connection error: {e}")
        return False

def test_tunnel_registry():
    """Test tunnel registry functionality"""
    print("📝 Testing tunnel registry...")
    
    try:
        # Import tunnel registry functions
        sys.path.append('.')
        from tunnel_registry import get_tunnel_url, set_tunnel_url
        
        # Test setting tunnel URL
        success = set_tunnel_url(TEST_TUNNEL_URL)
        if success:
            print("✅ Tunnel URL set successfully")
        else:
            print("❌ Failed to set tunnel URL")
            return False
        
        # Test getting tunnel URL
        retrieved_url = get_tunnel_url()
        if retrieved_url == TEST_TUNNEL_URL:
            print(f"✅ Tunnel URL retrieved successfully: {retrieved_url}")
            return True
        else:
            print(f"❌ Retrieved URL doesn't match: {retrieved_url} != {TEST_TUNNEL_URL}")
            return False
            
    except Exception as e:
        print(f"❌ Tunnel registry error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🚀 Starting Comprehensive Integration Test")
    print("=" * 60)
    
    tests = [
        ("Direct ComfyUI Connection", test_direct_comfyui_connection),
        ("Tunnel Registry", test_tunnel_registry),
        ("Tunnel Registration", test_tunnel_registration),
        ("Health Endpoint", test_health_endpoint),
        ("GPU Status", test_gpu_status),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results[test_name] = False
        
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integration is working correctly!")
        print("\n🚀 Next Steps:")
        print("1. Deploy your updated app to Railway")
        print("2. Start your local ComfyUI")
        print("3. Run start_production_cloudflare.bat")
        print("4. Test image generation on your Railway app")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure ComfyUI is running locally on port 8188")
        print("2. Verify Cloudflare tunnel is active")
        print("3. Check Railway environment variables")
        print("4. Ensure tunnel URL is accessible")
        return False

if __name__ == "__main__":
    print("🧪 Railway + Local ComfyUI Integration Test")
    print(f"Railway URL: {RAILWAY_URL}")
    print(f"Test Tunnel URL: {TEST_TUNNEL_URL}")
    print(f"Tunnel Secret: {TUNNEL_SECRET}")
    print()
    
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 Integration test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Integration test failed!")
        sys.exit(1)
