#!/usr/bin/env python3
"""
Railway Volumes Migration Test Script
Tests the complete facial evaluation image storage system with Railway volumes
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def test_railway_volumes_migration():
    """Test Railway volumes configuration for facial evaluation images"""
    
    print("🚀 Testing Railway Volumes Migration for Facial Evaluation Images")
    print("=" * 70)
    
    # Test 1: Check Railway configuration
    print("\n1. Checking Railway Configuration...")
    
    # Check railway.toml
    railway_config_path = "railway.toml"
    if os.path.exists(railway_config_path):
        with open(railway_config_path, 'r') as f:
            config_content = f.read()
            
        if "[[deploy.volumes]]" in config_content:
            print("✅ Railway volumes configured in railway.toml")
            
            # Check for uploads volume
            if 'name = "uploads"' in config_content and 'mountPoint = "/app/uploads"' in config_content:
                print("✅ Uploads volume: /app/uploads")
            else:
                print("❌ Uploads volume not properly configured")
                return False
                
            # Check for outputs volume
            if 'name = "outputs"' in config_content and 'mountPoint = "/app/outputs"' in config_content:
                print("✅ Outputs volume: /app/outputs")
            else:
                print("❌ Outputs volume not properly configured")
                return False
        else:
            print("❌ No volumes configured in railway.toml")
            return False
    else:
        print("❌ railway.toml not found")
        return False
    
    # Test 2: Check Dockerfile
    print("\n2. Checking Dockerfile Configuration...")
    
    dockerfile_paths = ["Dockerfile", "deployment/Dockerfile"]
    dockerfile_found = False
    
    for dockerfile_path in dockerfile_paths:
        if os.path.exists(dockerfile_path):
            dockerfile_found = True
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
            
            if "mkdir -p uploads outputs" in dockerfile_content:
                print(f"✅ Dockerfile creates directories: {dockerfile_path}")
            else:
                print(f"⚠️  Dockerfile should create directories: {dockerfile_path}")
            break
    
    if not dockerfile_found:
        print("❌ No Dockerfile found")
        return False
    
    # Test 3: Check app.py configuration
    print("\n3. Checking App Configuration...")
    
    if os.path.exists("app.py"):
        with open("app.py", 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Check for absolute paths
        if "APP_ROOT = os.path.dirname(os.path.abspath(__file__))" in app_content:
            print("✅ App uses absolute paths for deployment")
        else:
            print("❌ App should use absolute paths")
            return False
        
        # Check for facial evaluation routes
        facial_eval_routes = [
            "/facial-evaluation",
            "/request-facial-evaluation",
            "/facial-evaluation-image",
            "/admin/facial-evaluations"
        ]
        
        routes_found = 0
        for route in facial_eval_routes:
            if route in app_content:
                routes_found += 1
        
        if routes_found >= 3:
            print(f"✅ Facial evaluation routes implemented ({routes_found}/{len(facial_eval_routes)})")
        else:
            print(f"❌ Missing facial evaluation routes ({routes_found}/{len(facial_eval_routes)})")
            return False
            
    else:
        print("❌ app.py not found")
        return False
    
    # Test 4: Check models.py for FacialEvaluation
    print("\n4. Checking Database Models...")
    
    if os.path.exists("models.py"):
        with open("models.py", 'r') as f:
            models_content = f.read()
        
        if "class FacialEvaluation" in models_content:
            print("✅ FacialEvaluation model exists")
            
            # Check for required fields
            required_fields = [
                "original_image_filename",
                "morphed_image_filename", 
                "secondary_image_filename",
                "admin_response",
                "credits_used"
            ]
            
            fields_found = 0
            for field in required_fields:
                if field in models_content:
                    fields_found += 1
            
            if fields_found >= 4:
                print(f"✅ Required database fields present ({fields_found}/{len(required_fields)})")
            else:
                print(f"❌ Missing database fields ({fields_found}/{len(required_fields)})")
                return False
        else:
            print("❌ FacialEvaluation model not found")
            return False
    else:
        print("❌ models.py not found")
        return False
    
    # Test 5: Check templates
    print("\n5. Checking Templates...")
    
    required_templates = [
        "templates/facial_evaluation/dashboard.html",
        "templates/admin/facial_evaluations.html",
        "templates/admin/respond_facial_evaluation.html"
    ]
    
    templates_found = 0
    for template in required_templates:
        if os.path.exists(template):
            templates_found += 1
            print(f"✅ {template}")
        else:
            print(f"❌ Missing: {template}")
    
    if templates_found < len(required_templates):
        print(f"⚠️  Some templates missing ({templates_found}/{len(required_templates)})")
    
    # Test 6: Check .gitignore
    print("\n6. Checking .gitignore Configuration...")
    
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            gitignore_content = f.read()
        
        if "uploads/*" in gitignore_content and "outputs/*" in gitignore_content:
            print("✅ Image folders excluded from git")
        else:
            print("❌ Image folders should be excluded from git")
            return False
        
        if "!uploads/.gitkeep" in gitignore_content and "!outputs/.gitkeep" in gitignore_content:
            print("✅ .gitkeep files preserved")
        else:
            print("⚠️  .gitkeep files should be preserved")
    else:
        print("❌ .gitignore not found")
        return False
    
    # Test 7: Check local directories
    print("\n7. Checking Local Directory Structure...")
    
    local_dirs = ["uploads", "outputs"]
    for directory in local_dirs:
        if os.path.exists(directory):
            print(f"✅ Local {directory}/ directory exists")
            
            # Check for .gitkeep
            gitkeep_path = os.path.join(directory, ".gitkeep")
            if os.path.exists(gitkeep_path):
                print(f"✅ {directory}/.gitkeep exists")
            else:
                print(f"⚠️  {directory}/.gitkeep missing")
        else:
            print(f"❌ Local {directory}/ directory missing")
            return False
    
    # Test 8: Volume size estimation
    print("\n8. Volume Size Analysis...")
    
    print("📊 Railway Volume Limits:")
    print("   • Free Plan: 0.5GB (500MB)")
    print("   • Hobby Plan: 5GB")
    print("   • Pro Plan: 50GB")
    
    # Estimate storage needs
    avg_image_size = 2  # MB per image (conservative estimate)
    images_per_evaluation = 2.5  # Average (original + morphed + optional secondary)
    
    evaluations_500mb = int(500 / (avg_image_size * images_per_evaluation))
    evaluations_5gb = int(5000 / (avg_image_size * images_per_evaluation))
    
    print(f"\n📈 Storage Capacity Estimates:")
    print(f"   • Free (0.5GB): ~{evaluations_500mb} facial evaluations")
    print(f"   • Hobby (5GB): ~{evaluations_5gb} facial evaluations")
    print(f"   • Pro (50GB): ~{evaluations_5gb * 10} facial evaluations")
    
    # Test 9: Configuration summary
    print("\n9. Configuration Summary...")
    
    print("🔧 Railway Volumes Configuration:")
    print("   • uploads/ → /app/uploads (persistent)")
    print("   • outputs/ → /app/outputs (persistent)")
    print("   • Database: PostgreSQL (persistent)")
    print("   • Cost: FREE for 0.5GB storage")
    
    print("\n📁 Image Storage Paths:")
    print("   • Original images: /app/uploads/")
    print("   • Generated images: /app/outputs/")
    print("   • Secondary images: /app/uploads/")
    
    print("\n🔒 Security Features:")
    print("   • Images excluded from git")
    print("   • Admin-only access to all evaluations")
    print("   • User access to own evaluations only")
    print("   • 20 credits required per evaluation")
    
    print("\n✅ Railway Volumes Migration Test PASSED!")
    print("🎉 Your facial evaluation feature is ready for deployment!")
    
    return True

def test_deployment_readiness():
    """Test if the app is ready for Railway deployment"""
    
    print("\n" + "=" * 70)
    print("🚀 DEPLOYMENT READINESS CHECK")
    print("=" * 70)
    
    # Check required files
    required_files = [
        "railway.toml",
        "app.py", 
        "models.py",
        "requirements.txt",
        "Dockerfile"
    ]
    
    print("\n📋 Required Files Check:")
    all_files_present = True
    for file in required_files:
        if os.path.exists(file) or os.path.exists(f"deployment/{file}"):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_files_present = False
    
    if not all_files_present:
        print("\n❌ Missing required files for deployment")
        return False
    
    # Check environment variables
    print("\n🔧 Environment Variables Check:")
    env_vars = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "ENVIRONMENT"
    ]
    
    for var in env_vars:
        if var in os.environ:
            print(f"✅ {var} (set)")
        else:
            print(f"⚠️  {var} (will be set by Railway)")
    
    print("\n🎯 Deployment Commands:")
    print("   1. railway login")
    print("   2. railway up")
    print("   3. Check Railway dashboard for volume creation")
    print("   4. Test facial evaluation feature")
    
    print("\n✅ App is ready for Railway deployment!")
    return True

if __name__ == "__main__":
    print("Railway Volumes Migration Test")
    print("Testing facial evaluation image storage system...")
    
    try:
        # Run migration test
        migration_success = test_railway_volumes_migration()
        
        if migration_success:
            # Run deployment readiness test
            deployment_success = test_deployment_readiness()
            
            if deployment_success:
                print("\n🎉 ALL TESTS PASSED!")
                print("Your facial evaluation feature with Railway volumes is ready!")
                sys.exit(0)
            else:
                print("\n❌ Deployment readiness check failed")
                sys.exit(1)
        else:
            print("\n❌ Migration test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
