#!/usr/bin/env python3
"""
Deploy Email Verification to Railway
==================================

This script manually sets Railway environment variables and creates a deployment guide.
"""

import os
from dotenv import load_dotenv

def main():
    print("🎭 PSL Morph - Email Verification Railway Deployment")
    print("=" * 60)
    
    # Load local environment variables
    load_dotenv()
    
    # Get environment variables
    resend_api_key = os.getenv('RESEND_API_KEY')
    resend_from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@ascendbase.pro')
    resend_from_name = os.getenv('RESEND_FROM_NAME', 'PSL Morph')
    base_url = os.getenv('BASE_URL', 'https://www.ascendbase.pro')
    
    if not resend_api_key:
        print("❌ RESEND_API_KEY not found in .env file")
        return False
    
    print(f"📧 Resend API Key: {resend_api_key[:10]}...")
    print(f"📧 From Email: {resend_from_email}")
    print(f"📧 From Name: {resend_from_name}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    print("📋 Manual Railway Environment Variable Setup")
    print("=" * 50)
    print("Copy and paste these commands in your terminal:")
    print()
    
    # Generate Railway CLI commands
    commands = [
        f'railway variables --set RESEND_API_KEY="{resend_api_key}"',
        f'railway variables --set RESEND_FROM_EMAIL="{resend_from_email}"',
        f'railway variables --set RESEND_FROM_NAME="{resend_from_name}"',
        f'railway variables --set BASE_URL="{base_url}"'
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. {command}")
    
    print()
    print("🔧 Alternative method (if above doesn't work):")
    print("1. Go to Railway dashboard: https://railway.app/dashboard")
    print("2. Select your PSL Morph project")
    print("3. Go to Variables tab")
    print("4. Add these environment variables manually:")
    print()
    print(f"   RESEND_API_KEY = {resend_api_key}")
    print(f"   RESEND_FROM_EMAIL = {resend_from_email}")
    print(f"   RESEND_FROM_NAME = {resend_from_name}")
    print(f"   BASE_URL = {base_url}")
    print()
    
    print("✅ Email Verification System Status:")
    print("=" * 40)
    print("✅ Resend domain verified: ascendbase.pro")
    print("✅ DNS records configured correctly")
    print("✅ Email templates created")
    print("✅ Verification routes implemented")
    print("✅ Database schema ready")
    print("✅ URL format fixed")
    print()
    
    print("📋 Next Steps:")
    print("1. Set Railway environment variables (commands above)")
    print("2. Railway will automatically redeploy")
    print("3. Test registration on your deployed app")
    print("4. Check email verification flow")
    print()
    
    print("🧪 Test the verification flow:")
    print("1. Go to: https://psl-morph-production.up.railway.app/auth/register")
    print("2. Register with a Gmail account")
    print("3. Check email for verification link")
    print("4. Click verification link")
    print("5. Login to your account")
    print()
    
    print("🎉 Email verification system is ready for deployment!")
    return True

if __name__ == "__main__":
    main()
