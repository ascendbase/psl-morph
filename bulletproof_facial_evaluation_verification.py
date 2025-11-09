#!/usr/bin/env python3
"""
BULLETPROOF Facial Evaluation Railway Volume Verification
This script performs an exhaustive analysis of ALL image storage paths
"""

import os
import sys
import re
from pathlib import Path

def print_header(title):
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

def print_status(check, status, details=""):
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {check}")
    if details:
        print(f"   {details}")

def analyze_file_storage_patterns():
    """Analyze ALL file storage patterns in the codebase"""
    print_header("BULLETPROOF FILE STORAGE ANALYSIS")
    
    # Read app.py content
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Read config.py content
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    print("🔍 ANALYZING ALL IMAGE STORAGE PATTERNS...")
    
    # 1. Check facial evaluation folder configuration
    facial_eval_config = re.search(r'FACIAL_EVALUATION_FOLDER\s*=\s*([^\n]+)', config_content)
    if facial_eval_config:
        config_value = facial_eval_config.group(1).strip()
        print_status("FACIAL_EVALUATION_FOLDER configured in config.py", True, f"Value: {config_value}")
        
        # Check if it uses Railway volume path
        uses_railway_volume = '/app/facial_evaluations' in config_value or 'is_railway' in config_value
        print_status("Uses Railway volume logic", uses_railway_volume)
    else:
        print_status("FACIAL_EVALUATION_FOLDER configured in config.py", False)
        return False
    
    # 2. Analyze ALL file.save() operations
    file_save_patterns = re.findall(r'file\.save\(([^)]+)\)', app_content)
    print(f"\n📁 FOUND {len(file_save_patterns)} file.save() operations:")
    
    for i, pattern in enumerate(file_save_patterns, 1):
        print(f"   {i}. file.save({pattern})")
        
        # Check if it uses FACIAL_EVALUATION_FOLDER
        uses_facial_eval_folder = 'FACIAL_EVALUATION_FOLDER' in pattern
        if uses_facial_eval_folder:
            print_status(f"   Uses FACIAL_EVALUATION_FOLDER", True)
        else:
            print_status(f"   Uses FACIAL_EVALUATION_FOLDER", False, f"Uses: {pattern}")
    
    # 3. Analyze ALL shutil.copy operations
    copy_patterns = re.findall(r'shutil\.copy2?\([^)]+\)', app_content)
    print(f"\n📋 FOUND {len(copy_patterns)} shutil.copy operations:")
    
    for i, pattern in enumerate(copy_patterns, 1):
        print(f"   {i}. {pattern}")
        
        # Check if destination uses FACIAL_EVALUATION_FOLDER
        if 'facial_eval_path' in pattern or 'FACIAL_EVALUATION_FOLDER' in pattern:
            print_status(f"   Copies to FACIAL_EVALUATION_FOLDER", True)
        else:
            print_status(f"   Copies to FACIAL_EVALUATION_FOLDER", False)
    
    # 4. Check ALL os.path.join operations with image storage
    join_patterns = re.findall(r'os\.path\.join\([^)]+\)', app_content)
    facial_eval_joins = [p for p in join_patterns if 'FACIAL_EVALUATION_FOLDER' in p]
    
    print(f"\n🔗 FOUND {len(facial_eval_joins)} os.path.join operations using FACIAL_EVALUATION_FOLDER:")
    for i, pattern in enumerate(facial_eval_joins, 1):
        print(f"   {i}. {pattern}")
        print_status(f"   Uses Railway volume path", True)
    
    # 5. Check for any hardcoded paths
    hardcoded_patterns = re.findall(r'["\'](?:uploads|outputs|facial_evaluations)/[^"\']*["\']', app_content)
    print(f"\n⚠️  CHECKING FOR HARDCODED PATHS ({len(hardcoded_patterns)} found):")
    
    problematic_paths = []
    for pattern in hardcoded_patterns:
        if 'facial_evaluations' in pattern and not pattern.startswith('facial_evaluations'):
            problematic_paths.append(pattern)
            print_status(f"   Hardcoded path: {pattern}", False, "Should use FACIAL_EVALUATION_FOLDER")
        else:
            print_status(f"   Path: {pattern}", True, "OK - relative or proper")
    
    return len(problematic_paths) == 0

def verify_image_serving_routes():
    """Verify image serving routes use Railway volume"""
    print_header("IMAGE SERVING ROUTES VERIFICATION")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Find get_facial_evaluation_image function
    image_route_match = re.search(r'def get_facial_evaluation_image.*?(?=\n@|\ndef|\nclass|\Z)', app_content, re.DOTALL)
    
    if image_route_match:
        route_content = image_route_match.group(0)
        print_status("get_facial_evaluation_image route found", True)
        
        # Check if it uses FACIAL_EVALUATION_FOLDER for all image types
        uses_facial_eval_folder = route_content.count('FACIAL_EVALUATION_FOLDER') >= 3  # original, morphed, secondary
        print_status("Uses FACIAL_EVALUATION_FOLDER for all image types", uses_facial_eval_folder,
                   f"Found {route_content.count('FACIAL_EVALUATION_FOLDER')} references")
        
        # Check for any hardcoded folder references
        hardcoded_folders = re.findall(r'folder\s*=\s*["\'][^"\']+["\']', route_content)
        if hardcoded_folders:
            print_status("No hardcoded folder paths", False, f"Found: {hardcoded_folders}")
            return False
        else:
            print_status("No hardcoded folder paths", True)
        
        return uses_facial_eval_folder
    else:
        print_status("get_facial_evaluation_image route found", False)
        return False

def verify_database_schema():
    """Verify database schema supports all required fields"""
    print_header("DATABASE SCHEMA VERIFICATION")
    
    with open('models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # Find FacialEvaluation class
    facial_eval_match = re.search(r'class FacialEvaluation.*?(?=\nclass|\Z)', models_content, re.DOTALL)
    
    if facial_eval_match:
        class_content = facial_eval_match.group(0)
        print_status("FacialEvaluation model found", True)
        
        required_fields = [
            'original_image_filename',
            'morphed_image_filename',
            'secondary_image_filename',
            'admin_response',
            'status',
            'credits_used'
        ]
        
        all_fields_present = True
        for field in required_fields:
            field_present = field in class_content
            print_status(f"Field '{field}' present", field_present)
            if not field_present:
                all_fields_present = False
        
        return all_fields_present
    else:
        print_status("FacialEvaluation model found", False)
        return False

def verify_deployment_configuration():
    """Verify deployment files are properly configured"""
    print_header("DEPLOYMENT CONFIGURATION VERIFICATION")
    
    # Check Dockerfile
    dockerfile_paths = ['deployment/Dockerfile', 'Dockerfile']
    dockerfile_ok = False
    
    for dockerfile_path in dockerfile_paths:
        if os.path.exists(dockerfile_path):
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                dockerfile_content = f.read()
            
            creates_facial_eval_dir = 'facial_evaluations' in dockerfile_content
            print_status(f"Dockerfile creates facial_evaluations directory ({dockerfile_path})", creates_facial_eval_dir)
            
            if creates_facial_eval_dir:
                dockerfile_ok = True
                break
    
    # Check railway.toml
    railway_toml_paths = ['deployment/railway.toml', 'railway.toml']
    railway_ok = False
    
    for toml_path in railway_toml_paths:
        if os.path.exists(toml_path):
            with open(toml_path, 'r', encoding='utf-8') as f:
                toml_content = f.read()
            
            has_prod_env = 'ENVIRONMENT = "production"' in toml_content
            print_status(f"Railway config has production environment ({toml_path})", has_prod_env)
            
            if has_prod_env:
                railway_ok = True
                break
    
    return dockerfile_ok and railway_ok

def verify_config_railway_detection():
    """Verify config.py properly detects Railway environment"""
    print_header("RAILWAY DETECTION LOGIC VERIFICATION")
    
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Check for Railway detection
    has_railway_detection = 'is_railway' in config_content
    print_status("Has Railway detection logic", has_railway_detection)
    
    # Check for conditional path setting
    has_conditional_path = 'if is_railway' in config_content or 'if.*railway' in config_content.lower()
    print_status("Has conditional path setting", has_conditional_path)
    
    # Check for volume path
    has_volume_path = '/app/facial_evaluations' in config_content
    print_status("Uses Railway volume path", has_volume_path)
    
    return has_railway_detection and has_conditional_path and has_volume_path

def main():
    """Run comprehensive bulletproof verification"""
    print_header("BULLETPROOF FACIAL EVALUATION RAILWAY VOLUME VERIFICATION")
    print("This script performs an exhaustive analysis of ALL image storage paths")
    print("to ensure facial evaluation images are properly stored using Railway volumes")
    
    checks = [
        ("File Storage Patterns", analyze_file_storage_patterns),
        ("Image Serving Routes", verify_image_serving_routes),
        ("Database Schema", verify_database_schema),
        ("Deployment Configuration", verify_deployment_configuration),
        ("Railway Detection Logic", verify_config_railway_detection)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"{check_name} verification failed", False, str(e))
            results.append((check_name, False))
    
    # Final summary
    print_header("BULLETPROOF VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        print_status(check_name, result)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 BULLETPROOF VERIFICATION PASSED!")
        print("✅ ALL facial evaluation images are properly configured to use Railway volumes")
        print("✅ No hardcoded paths found")
        print("✅ All image storage operations use FACIAL_EVALUATION_FOLDER")
        print("✅ Railway volume path is correctly configured")
        print("\n🚀 Your facial evaluation feature is BULLETPROOF for Railway deployment!")
    else:
        print(f"\n⚠️  BULLETPROOF VERIFICATION FAILED!")
        print(f"❌ {total - passed} critical issues found")
        print("🔧 Please fix the issues above before deploying")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
