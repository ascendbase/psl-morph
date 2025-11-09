#!/usr/bin/env python3
"""
Comprehensive Facial Evaluation Deployment Verification Script
This script verifies that all components are properly configured for Railway deployment
"""

import os
import sys
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_status(check, status, details=""):
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {check}")
    if details:
        print(f"   {details}")

def verify_config_file():
    """Verify config.py has proper Railway volume configuration"""
    print_header("CONFIG.PY VERIFICATION")
    
    try:
        # Import config to test
        sys.path.insert(0, '.')
        import config
        
        # Check Railway detection logic
        has_railway_detection = hasattr(config, 'is_railway')
        print_status("Railway detection logic exists", has_railway_detection)
        
        # Check facial evaluation folder configuration
        has_facial_eval_folder = hasattr(config, 'FACIAL_EVALUATION_FOLDER')
        print_status("FACIAL_EVALUATION_FOLDER configured", has_facial_eval_folder)
        
        if has_facial_eval_folder:
            folder_path = config.FACIAL_EVALUATION_FOLDER
            print_status("Facial evaluation folder path", True, f"Path: {folder_path}")
            
            # Check if it's using Railway volume path when on Railway
            if hasattr(config, 'is_railway') and config.is_railway:
                uses_volume_path = folder_path == '/app/facial_evaluations'
                print_status("Uses Railway volume path", uses_volume_path, 
                           f"Expected: /app/facial_evaluations, Got: {folder_path}")
            else:
                uses_local_path = folder_path == 'facial_evaluations'
                print_status("Uses local development path", uses_local_path,
                           f"Expected: facial_evaluations, Got: {folder_path}")
        
        return True
        
    except Exception as e:
        print_status("Config import failed", False, str(e))
        return False

def verify_app_file():
    """Verify app.py doesn't override config settings"""
    print_header("APP.PY VERIFICATION")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Check for proper facial evaluation folder handling
        has_proper_handling = 'if not os.path.isabs(FACIAL_EVALUATION_FOLDER):' in app_content
        print_status("Proper facial evaluation folder handling", has_proper_handling)
        
        # Check that it doesn't override with absolute path
        bad_override = 'FACIAL_EVALUATION_FOLDER = os.path.join(APP_ROOT, FACIAL_EVALUATION_FOLDER)' in app_content and 'if not os.path.isabs' not in app_content
        print_status("No improper path override", not bad_override)
        
        # Check for Railway volume configuration import
        imports_config = 'from config import *' in app_content
        print_status("Imports config properly", imports_config)
        
        return True
        
    except Exception as e:
        print_status("App.py verification failed", False, str(e))
        return False

def verify_dockerfile():
    """Verify Dockerfile creates facial_evaluations directory"""
    print_header("DOCKERFILE VERIFICATION")
    
    dockerfile_paths = ['deployment/Dockerfile', 'Dockerfile']
    dockerfile_found = False
    
    for dockerfile_path in dockerfile_paths:
        if os.path.exists(dockerfile_path):
            dockerfile_found = True
            try:
                with open(dockerfile_path, 'r', encoding='utf-8') as f:
                    dockerfile_content = f.read()
                
                # Check for facial_evaluations directory creation
                creates_facial_eval_dir = 'facial_evaluations' in dockerfile_content
                print_status(f"Creates facial_evaluations directory ({dockerfile_path})", 
                           creates_facial_eval_dir)
                
                # Check for proper mkdir command
                has_mkdir = 'mkdir -p' in dockerfile_content and 'facial_evaluations' in dockerfile_content
                print_status(f"Has proper mkdir command ({dockerfile_path})", has_mkdir)
                
                break
                
            except Exception as e:
                print_status(f"Dockerfile read failed ({dockerfile_path})", False, str(e))
    
    if not dockerfile_found:
        print_status("Dockerfile found", False, "No Dockerfile found in expected locations")
    
    return dockerfile_found

def verify_railway_config():
    """Verify Railway configuration files"""
    print_header("RAILWAY CONFIGURATION VERIFICATION")
    
    # Check railway.toml
    railway_toml_paths = ['deployment/railway.toml', 'railway.toml']
    railway_config_found = False
    
    for toml_path in railway_toml_paths:
        if os.path.exists(toml_path):
            railway_config_found = True
            print_status(f"Railway config found ({toml_path})", True)
            
            try:
                with open(toml_path, 'r', encoding='utf-8') as f:
                    toml_content = f.read()
                
                # Check for production environment
                has_prod_env = 'ENVIRONMENT = "production"' in toml_content
                print_status("Production environment configured", has_prod_env)
                
                # Check for health check
                has_health_check = 'healthcheckPath' in toml_content
                print_status("Health check configured", has_health_check)
                
            except Exception as e:
                print_status(f"Railway config read failed ({toml_path})", False, str(e))
            break
    
    if not railway_config_found:
        print_status("Railway config found", False, "No railway.toml found")
    
    return railway_config_found

def verify_templates():
    """Verify facial evaluation templates exist"""
    print_header("TEMPLATE VERIFICATION")
    
    required_templates = [
        'templates/facial_evaluation/dashboard.html',
        'templates/admin/facial_evaluations.html',
        'templates/admin/respond_facial_evaluation.html'
    ]
    
    all_templates_exist = True
    
    for template_path in required_templates:
        exists = os.path.exists(template_path)
        print_status(f"Template exists: {template_path}", exists)
        if not exists:
            all_templates_exist = False
    
    return all_templates_exist

def verify_database_models():
    """Verify database models are properly configured"""
    print_header("DATABASE MODEL VERIFICATION")
    
    try:
        with open('models.py', 'r', encoding='utf-8') as f:
            models_content = f.read()
        
        # Check for FacialEvaluation model
        has_facial_eval_model = 'class FacialEvaluation' in models_content
        print_status("FacialEvaluation model exists", has_facial_eval_model)
        
        # Check for required fields
        required_fields = [
            'original_image_filename',
            'morphed_image_filename', 
            'secondary_image_filename',
            'admin_response',
            'status',
            'credits_used'
        ]
        
        for field in required_fields:
            has_field = field in models_content
            print_status(f"Has {field} field", has_field)
        
        return has_facial_eval_model
        
    except Exception as e:
        print_status("Models verification failed", False, str(e))
        return False

def verify_local_directories():
    """Verify local directories exist"""
    print_header("LOCAL DIRECTORY VERIFICATION")
    
    required_dirs = [
        'facial_evaluations',
        'uploads',
        'outputs',
        'templates/facial_evaluation',
        'templates/admin'
    ]
    
    all_dirs_exist = True
    
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        print_status(f"Directory exists: {dir_path}", exists)
        if not exists:
            all_dirs_exist = False
            # Try to create it
            try:
                os.makedirs(dir_path, exist_ok=True)
                print_status(f"Created directory: {dir_path}", True)
            except Exception as e:
                print_status(f"Failed to create: {dir_path}", False, str(e))
    
    return all_dirs_exist

def verify_requirements():
    """Verify requirements.txt has necessary dependencies"""
    print_header("REQUIREMENTS VERIFICATION")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements_content = f.read()
        
        required_packages = [
            'Flask',
            'Flask-Login',
            'Flask-SQLAlchemy',
            'Pillow',
            'requests',
            'mistune'
        ]
        
        all_packages_found = True
        
        for package in required_packages:
            found = package.lower() in requirements_content.lower()
            print_status(f"Package {package} in requirements", found)
            if not found:
                all_packages_found = False
        
        return all_packages_found
        
    except Exception as e:
        print_status("Requirements verification failed", False, str(e))
        return False

def main():
    """Run all verification checks"""
    print_header("FACIAL EVALUATION DEPLOYMENT VERIFICATION")
    print("This script verifies that all components are properly configured for Railway deployment")
    
    checks = [
        ("Config File", verify_config_file),
        ("App File", verify_app_file),
        ("Dockerfile", verify_dockerfile),
        ("Railway Config", verify_railway_config),
        ("Templates", verify_templates),
        ("Database Models", verify_database_models),
        ("Local Directories", verify_local_directories),
        ("Requirements", verify_requirements)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"{check_name} verification failed", False, str(e))
            results.append((check_name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        print_status(check_name, result)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Your facial evaluation feature is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Commit and push your changes to GitHub")
        print("2. Deploy to Railway")
        print("3. Create the facial_evaluations volume in Railway dashboard")
        print("4. Mount the volume to /app/facial_evaluations")
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please fix the issues above before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
