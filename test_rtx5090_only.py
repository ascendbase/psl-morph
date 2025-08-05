#!/usr/bin/env python3
"""
Test script to verify the app is configured to use ONLY RTX 5090
"""

import os
import sys
from config import *

def test_rtx5090_configuration():
    """Test that the app is configured to use RTX 5090 ONLY"""
    print("🧪 Testing RTX 5090 ONLY Configuration")
    print("=" * 50)
    
    # Check environment variables
    print("1. Environment Variables:")
    print(f"   USE_CLOUD_GPU: {USE_CLOUD_GPU}")
    print(f"   USE_RUNPOD_POD: {USE_RUNPOD_POD}")
    print(f"   RUNPOD_POD_URL: {RUNPOD_POD_URL}")
    print(f"   RUNPOD_POD_PORT: {RUNPOD_POD_PORT}")
    print(f"   COMFYUI_URL: {COMFYUI_URL}")
    print()
    
    # Verify configuration
    errors = []
    
    if not USE_CLOUD_GPU:
        errors.append("❌ USE_CLOUD_GPU is False - should be True for RTX 5090")
    else:
        print("✅ USE_CLOUD_GPU is True")
    
    if not USE_RUNPOD_POD:
        errors.append("❌ USE_RUNPOD_POD is False - should be True for RTX 5090")
    else:
        print("✅ USE_RUNPOD_POD is True")
    
    if not RUNPOD_POD_URL:
        errors.append("❌ RUNPOD_POD_URL is empty")
    elif "choa76vtevld8t-8188.proxy.runpod.net" not in RUNPOD_POD_URL:
        errors.append(f"❌ RUNPOD_POD_URL incorrect: {RUNPOD_POD_URL}")
    else:
        print("✅ RUNPOD_POD_URL is correct")
    
    if "https://choa76vtevld8t-8188.proxy.runpod.net" not in COMFYUI_URL:
        errors.append(f"❌ COMFYUI_URL incorrect: {COMFYUI_URL}")
    else:
        print("✅ COMFYUI_URL is correct")
    
    print()
    
    # Test GPU client initialization
    print("2. GPU Client Initialization:")
    try:
        if USE_CLOUD_GPU:
            if USE_RUNPOD_POD:
                from runpod_pod_client import RunPodPodClient
                gpu_client = RunPodPodClient(
                    pod_url=RUNPOD_POD_URL,
                    pod_port=RUNPOD_POD_PORT
                )
                print("✅ RunPod Pod client initialized successfully")
                
                # Test connection
                if gpu_client.test_connection():
                    print("✅ RTX 5090 connection successful!")
                else:
                    errors.append("❌ RTX 5090 connection failed")
            else:
                errors.append("❌ USE_RUNPOD_POD is False but USE_CLOUD_GPU is True")
        else:
            errors.append("❌ USE_CLOUD_GPU is False - will use local GPU instead of RTX 5090")
    except Exception as e:
        errors.append(f"❌ GPU client initialization failed: {e}")
    
    print()
    
    # Final result
    if errors:
        print("❌ CONFIGURATION ERRORS FOUND:")
        for error in errors:
            print(f"   {error}")
        print()
        print("🚨 The app is NOT configured to use RTX 5090 exclusively!")
        print("   Please fix the configuration before running the app.")
        return False
    else:
        print("🎉 CONFIGURATION PERFECT!")
        print("✅ The app is correctly configured to use RTX 5090 ONLY!")
        print("✅ Local GPU processing is disabled.")
        print("✅ All face morphing will use the RTX 5090 cloud GPU.")
        return True

if __name__ == "__main__":
    print("🚀 RTX 5090 ONLY Configuration Test")
    print()
    
    success = test_rtx5090_configuration()
    
    if success:
        print()
        print("🎯 Ready to start the app with RTX 5090!")
        print("   Run: start_rtx5090.bat")
        print("   Login: ascendbase@gmail.com / morphpas")
        print("   The app will use ONLY the RTX 5090 cloud GPU.")
    else:
        print()
        print("⚠️  Please fix the configuration issues above.")
        
    print(f"\nTest completed.")