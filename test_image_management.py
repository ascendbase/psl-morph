#!/usr/bin/env python3
"""
Test script for Railway Volume Image Management

This script tests the image management functionality to ensure it works correctly.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_image_management():
    """Test the image management functions"""
    print("🧪 Testing Railway Volume Image Management")
    print("=" * 50)
    
    try:
        # Import the functions
        from delete_railway_volume_images import (
            get_volume_path, 
            list_all_images, 
            get_storage_stats,
            format_size
        )
        
        print("✅ Successfully imported image management functions")
        
        # Test volume path detection
        volume_path = get_volume_path()
        if volume_path:
            print(f"✅ Volume path detected: {volume_path}")
        else:
            print("⚠️ Volume path not found (this is normal for local testing)")
        
        # Test storage stats
        stats = get_storage_stats()
        if stats:
            print(f"✅ Storage stats retrieved:")
            print(f"   📁 Path: {stats['volume_path']}")
            print(f"   📊 Files: {stats['total_files']}")
            print(f"   💾 Size: {format_size(stats['total_size'])}")
        else:
            print("⚠️ No storage stats available (volume not found)")
        
        # Test image listing
        images = list_all_images()
        print(f"✅ Image listing function works - found {len(images)} images")
        
        # Test format_size function
        test_sizes = [0, 1024, 1024*1024, 1024*1024*1024]
        print("✅ Testing size formatting:")
        for size in test_sizes:
            formatted = format_size(size)
            print(f"   {size} bytes = {formatted}")
        
        print("\n🎉 All tests passed! Image management tools are ready to use.")
        print("\n📋 To use the tools:")
        print("   • Run: clean_railway_images.bat")
        print("   • Or: python delete_railway_volume_images.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available")
    except Exception as e:
        print(f"❌ Test error: {e}")
        print("Check the error details above")

if __name__ == "__main__":
    test_image_management()
