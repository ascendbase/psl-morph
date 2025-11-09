#!/usr/bin/env python3
"""
Update Railway Environment Variables for Resend Email Verification
================================================================

This script updates Railway environment variables to enable Resend email verification.
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    print("🎭 PSL Morph - Railway Environment Update for Resend")
    print("=" * 60)
    
    # Load local environment variables
    load_dotenv()
    
    # Get environment variables
    resend_api_key = os.getenv('RESEND_API_KEY')
    resend_from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@ascendbase.pro')
    resend_from_name = os.getenv('RESEND_FROM_NAME', 'PSL Morph')
    base_url = os.getenv('BASE_URL', 'https://psl-morph-production.up.railway.app')
    
    if not resend_api_key:
        print("❌ RESEND_API_KEY not found in .env file")
        return False
    
    print(f"📧 Resend API Key: {resend_api_key[:10]}...")
    print(f"📧 From Email: {resend_from_email}")
    print(f"📧 From Name: {resend_from_name}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Check if Railway CLI is installed
    print("🔍 Checking Railway CLI installation...")
    if not run_command("railway --version", "Railway CLI version check"):
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        return False
    
    # Login check
    print("🔍 Checking Railway login status...")
    if not run_command("railway whoami", "Railway login check"):
        print("❌ Not logged in to Railway. Please login first:")
        print("   railway login")
        return False
    
    # Set environment variables
    env_vars = [
        ("RESEND_API_KEY", resend_api_key),
        ("RESEND_FROM_EMAIL", resend_from_email),
        ("RESEND_FROM_NAME", resend_from_name),
        ("BASE_URL", base_url)
    ]
    
    print("🔧 Updating Railway environment variables...")
    success_count = 0
    
    for var_name, var_value in env_vars:
        if run_command(f'railway variables set {var_name}="{var_value}"', f"Setting {var_name}"):
            success_count += 1
        else:
            print(f"❌ Failed to set {var_name}")
    
    print()
    print(f"📊 Results: {success_count}/{len(env_vars)} environment variables updated successfully")
    
    if success_count == len(env_vars):
        print("🎉 All environment variables updated successfully!")
        print()
        print("📋 Next steps:")
        print("1. Railway will automatically redeploy with new environment variables")
        print("2. Wait for deployment to complete (usually 2-3 minutes)")
        print("3. Test email verification on your deployed app")
        print("4. Check Railway logs if there are any issues: railway logs")
        return True
    else:
        print("❌ Some environment variables failed to update")
        print("   Please check Railway CLI permissions and try again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
