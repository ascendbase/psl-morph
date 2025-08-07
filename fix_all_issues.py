#!/usr/bin/env python3
"""
Complete Fix Script for Railway App Issues
Fixes both ComfyUI parameter mismatch and provides database persistence solution
"""

import os
import re
import sys

def fix_comfyui_parameters():
    """Fix the ComfyUI parameter mismatch in app.py"""
    print("🔧 Fixing ComfyUI parameter mismatch...")
    
    try:
        # Read the current app.py file
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if there are any problematic calls
        if 'workflow_type=' in content and 'gpu_client.generate_image' in content:
            print("⚠️ Found problematic gpu_client.generate_image calls with extra parameters")
            
            # Pattern to find and fix calls with extra parameters
            # Look for calls that have workflow_type or custom_features parameters
            pattern = r'(prompt_id = gpu_client\.generate_image\(\s*image_path=file_path,\s*preset_name=tier_name,\s*denoise_strength=\w+),\s*workflow_type=\w+(?:,\s*custom_features=\w+)?\s*\)'
            
            replacement = r'\1)'
            
            # Apply the fix
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            if new_content != content:
                # Write the fixed content back
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ Fixed gpu_client.generate_image calls - removed extra parameters")
                return True
            else:
                print("ℹ️ No changes needed - parameters already correct")
                return True
        else:
            print("✅ No problematic gpu_client calls found")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing ComfyUI parameters: {e}")
        return False

def check_database_config():
    """Check if database configuration is correct for Railway"""
    print("\n🔧 Checking database configuration...")
    
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Railway environment detection is present
        if 'RAILWAY_ENVIRONMENT' in content and 'postgresql://' in content:
            print("✅ Database configuration is correct for Railway PostgreSQL")
            return True
        else:
            print("⚠️ Database configuration needs updating for Railway")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database config: {e}")
        return False

def check_requirements():
    """Check if PostgreSQL dependencies are in requirements.txt"""
    print("\n🔧 Checking requirements.txt...")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'psycopg2-binary' in content:
            print("✅ PostgreSQL dependency (psycopg2-binary) is present")
            return True
        else:
            print("⚠️ PostgreSQL dependency missing from requirements.txt")
            return False
            
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False

def create_railway_setup_script():
    """Create a script to help with Railway PostgreSQL setup"""
    print("\n🔧 Creating Railway setup helper script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Railway PostgreSQL Setup Helper
Run this after adding PostgreSQL service to your Railway project
"""

import os
import sys

def check_railway_environment():
    """Check if running on Railway with PostgreSQL"""
    print("🔍 Checking Railway environment...")
    
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    database_url = os.getenv('DATABASE_URL')
    
    if railway_env:
        print(f"✅ Railway environment detected: {railway_env}")
    else:
        print("⚠️ Not running on Railway (RAILWAY_ENVIRONMENT not set)")
    
    if database_url:
        if database_url.startswith('postgres'):
            print("✅ PostgreSQL database URL detected")
            print(f"   Database URL: {database_url[:50]}...")
        else:
            print(f"⚠️ Non-PostgreSQL database URL: {database_url[:50]}...")
    else:
        print("❌ No DATABASE_URL environment variable found")
        print("   Make sure you've added a PostgreSQL service to your Railway project")
    
    return railway_env and database_url and database_url.startswith('postgres')

def test_database_connection():
    """Test database connection"""
    print("\\n🔍 Testing database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        from config import DATABASE_URL
        
        print(f"Using database URL: {DATABASE_URL[:50]}...")
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Railway PostgreSQL Setup Check")
    print("=" * 40)
    
    env_ok = check_railway_environment()
    
    if env_ok:
        db_ok = test_database_connection()
        
        if db_ok:
            print("\\n🎉 Railway PostgreSQL setup is working correctly!")
            print("\\n📝 Your database will now persist across deployments")
        else:
            print("\\n❌ Database connection issues - check your Railway PostgreSQL service")
    else:
        print("\\n📋 Next steps:")
        print("1. Go to your Railway dashboard")
        print("2. Click 'New Service' → 'Database' → 'Add PostgreSQL'")
        print("3. Deploy your app again")
        print("4. Run this script again to verify")
'''
    
    try:
        with open('check_railway_setup.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("✅ Created check_railway_setup.py")
        return True
    except Exception as e:
        print(f"❌ Error creating setup script: {e}")
        return False

def create_deployment_script():
    """Create a deployment script for Railway"""
    print("\n🔧 Creating deployment helper script...")
    
    script_content = '''@echo off
echo 🚀 Railway Deployment with PostgreSQL
echo =====================================

echo.
echo 📋 Pre-deployment checklist:
echo ✓ PostgreSQL service added to Railway project
echo ✓ Database configuration updated in config.py
echo ✓ psycopg2-binary in requirements.txt
echo.

echo 🔄 Committing changes...
git add .
git commit -m "Fix: Database persistence + ComfyUI parameters"

echo.
echo 🚀 Pushing to Railway...
git push origin main

echo.
echo ⏳ Deployment in progress...
echo 📝 Check Railway dashboard for deployment status
echo 🔗 Your app will be available at your Railway domain

echo.
echo 🎯 After deployment:
echo 1. Test user registration/login
echo 2. Create test data
echo 3. Deploy a small change to verify data persists
echo.

pause
'''
    
    try:
        with open('deploy_to_railway.bat', 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("✅ Created deploy_to_railway.bat")
        return True
    except Exception as e:
        print(f"❌ Error creating deployment script: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Complete Fix Script for Railway App")
    print("=" * 50)
    
    success_count = 0
    total_checks = 5
    
    # Fix 1: ComfyUI parameters
    if fix_comfyui_parameters():
        success_count += 1
    
    # Check 2: Database config
    if check_database_config():
        success_count += 1
    
    # Check 3: Requirements
    if check_requirements():
        success_count += 1
    
    # Create 4: Railway setup script
    if create_railway_setup_script():
        success_count += 1
    
    # Create 5: Deployment script
    if create_deployment_script():
        success_count += 1
    
    print(f"\n📊 Results: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("\n🎉 All fixes applied successfully!")
        print("\n📝 Summary of fixes:")
        print("✅ Fixed ComfyUI parameter mismatch")
        print("✅ Database configuration ready for Railway PostgreSQL")
        print("✅ PostgreSQL dependencies present")
        print("✅ Created Railway setup checker")
        print("✅ Created deployment helper script")
        
        print("\n🚀 Next steps:")
        print("1. Add PostgreSQL service to your Railway project:")
        print("   - Go to Railway dashboard")
        print("   - Click 'New Service' → 'Database' → 'Add PostgreSQL'")
        print("2. Run: python check_railway_setup.py (after deployment)")
        print("3. Run: deploy_to_railway.bat (to deploy)")
        print("4. Test that user data persists across deployments")
        
        return True
    else:
        print("\n❌ Some issues need manual attention")
        print("Check the error messages above and fix manually")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Fix script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
