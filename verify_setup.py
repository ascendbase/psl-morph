#!/usr/bin/env python3
"""
Setup Verification Script for Face Morphing Web App
Run this to check if everything is configured correctly
"""

import os
import sys
import json
import requests
from pathlib import Path

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "END": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['END']}")

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print_status("Python version is compatible", "SUCCESS")
        return True
    else:
        print_status("Python 3.8+ required", "ERROR")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ["flask", "PIL", "requests"]
    missing = []
    
    for package in required_packages:
        try:
            if package == "PIL":
                import PIL
                print_status(f"Pillow (PIL) version: {PIL.__version__}", "SUCCESS")
            else:
                __import__(package)
                print_status(f"{package} is installed", "SUCCESS")
        except ImportError:
            missing.append(package)
            print_status(f"{package} is missing", "ERROR")
    
    if missing:
        print_status(f"Install missing packages: pip install {' '.join(missing)}", "WARNING")
        return False
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "app.py",
        "config.py", 
        "templates/index.html",
        "comfyui_workflows/workflow_fixed.json",
        "requirements.txt"
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"Found: {file_path}", "SUCCESS")
        else:
            missing.append(file_path)
            print_status(f"Missing: {file_path}", "ERROR")
    
    return len(missing) == 0

def check_directories():
    """Check if required directories exist"""
    required_dirs = ["uploads", "outputs", "templates", "comfyui_workflows"]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_status(f"Directory exists: {dir_path}", "SUCCESS")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print_status(f"Created directory: {dir_path}", "WARNING")

def check_workflow():
    """Check if workflow JSON is valid"""
    workflow_path = "comfyui_workflows/workflow_fixed.json"
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        # Check for required nodes
        required_nodes = ["1", "2", "5", "7", "9"]  # Checkpoint, LoRA, LoadImage, KSampler, ReActor
        
        for node_id in required_nodes:
            if node_id in workflow:
                print_status(f"Workflow node {node_id} found", "SUCCESS")
            else:
                print_status(f"Workflow node {node_id} missing", "ERROR")
                return False
        
        print_status("Workflow JSON is valid", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Workflow JSON error: {e}", "ERROR")
        return False

def check_models():
    """Check if model files exist"""
    model_files = [
        "base_models/real-dream-15.safetensors",
        "lora/chad_sd1.5.safetensors"
    ]
    
    for model_path in model_files:
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print_status(f"Model found: {model_path} ({size_mb:.1f} MB)", "SUCCESS")
        else:
            print_status(f"Model missing: {model_path}", "WARNING")

def check_comfyui_connection():
    """Check if ComfyUI is running and accessible"""
    comfyui_url = "http://127.0.0.1:8188"
    
    try:
        response = requests.get(f"{comfyui_url}/system_stats", timeout=5)
        if response.status_code == 200:
            print_status("ComfyUI API is accessible", "SUCCESS")
            
            # Try to get system info
            stats = response.json()
            if "system" in stats:
                print_status(f"ComfyUI system info available", "SUCCESS")
            
            return True
        else:
            print_status(f"ComfyUI returned status {response.status_code}", "WARNING")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("ComfyUI is not running or not accessible", "ERROR")
        print_status("Start ComfyUI with: python main.py --listen 127.0.0.1 --port 8188", "INFO")
        return False
    except Exception as e:
        print_status(f"ComfyUI connection error: {e}", "ERROR")
        return False

def check_comfyui_models():
    """Check if ComfyUI can access the required models"""
    # This would require ComfyUI API extensions to check model availability
    # For now, just check common ComfyUI directories
    
    comfyui_paths = [
        "D:/ComfyUI_windows_portable/ComfyUI",
        "../ComfyUI",
        "../../ComfyUI", 
        "./ComfyUI"
    ]
    
    for base_path in comfyui_paths:
        if os.path.exists(base_path):
            print_status(f"Found ComfyUI directory: {base_path}", "SUCCESS")
            
            # Check model directories
            model_dirs = {
                "checkpoints": os.path.join(base_path, "models", "checkpoints"),
                "loras": os.path.join(base_path, "models", "loras"),
                "insightface": os.path.join(base_path, "models", "insightface")
            }
            
            for name, path in model_dirs.items():
                if os.path.exists(path):
                    files = os.listdir(path)
                    print_status(f"ComfyUI {name} directory: {len(files)} files", "SUCCESS")
                else:
                    print_status(f"ComfyUI {name} directory missing", "WARNING")
            
            return True
    
    print_status("ComfyUI directory not found", "WARNING")
    return False

def main():
    """Run all verification checks"""
    print("🔍 Face Morphing Web App - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Required Files", check_files),
        ("Directories", check_directories),
        ("Workflow JSON", check_workflow),
        ("Model Files", check_models),
        ("ComfyUI Connection", check_comfyui_connection),
        ("ComfyUI Models", check_comfyui_models)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        results[check_name] = check_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("🎉 All checks passed! Your setup is ready.", "SUCCESS")
        print_status("Run 'python app.py' to start the web app", "INFO")
    else:
        print_status("⚠️  Some issues found. Check the details above.", "WARNING")
        print_status("See TROUBLESHOOTING.md for solutions", "INFO")

if __name__ == "__main__":
    main()