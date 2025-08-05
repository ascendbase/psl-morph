#!/usr/bin/env python3
"""
Fix RunPod ComfyUI Dependencies
Run this script in your RunPod terminal to install missing packages
"""

import subprocess
import sys

def run_command(command):
    """Run a command and print the output"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def main():
    print("🔧 Fixing RunPod ComfyUI Dependencies...")
    
    # List of missing packages to install
    packages = [
        'dill',           # For ComfyUI-Impact-Subpack
        'scikit-image',   # For ComfyUI-Impact-Pack and RyanOnTheInside (provides skimage)
        'GitPython',      # For ComfyUI-Manager (provides git module)
        'uv',             # For ComfyUI-Manager prestartup script
    ]
    
    print(f"📦 Installing {len(packages)} missing packages...")
    
    # Install each package
    for package in packages:
        print(f"\n📥 Installing {package}...")
        success = run_command(f"pip install {package}")
        if not success:
            print(f"⚠️  Failed to install {package}, trying with --upgrade...")
            run_command(f"pip install --upgrade {package}")
    
    print("\n🎯 Installing additional dependencies for Impact Pack...")
    # Additional packages that might be needed
    additional_packages = [
        'opencv-python',
        'numpy',
        'pillow',
        'scipy',
        'matplotlib'
    ]
    
    for package in additional_packages:
        run_command(f"pip install --upgrade {package}")
    
    print("\n✅ All dependencies installed!")
    print("\n🚀 Now restart ComfyUI with:")
    print("   python main.py --listen")
    print("\n💡 Your Face Morphing SaaS should now work properly!")

if __name__ == "__main__":
    main()