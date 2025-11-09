#!/usr/bin/env python3
"""
Test script for Brevo email functionality
This script tests the email verification system using Brevo API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from email_utils import generate_verification_token, send_verification_email, send_welcome_email
    print("✅ Successfully imported email_utils functions")
except ImportError as e:
    print(f"❌ Failed to import email_utils: {e}")
    sys.exit(1)

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        'BREVO_API_KEY',
        'BREVO_FROM_EMAIL', 
        'BREVO_FROM_NAME',
        'BASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask API key for security
            if 'API_KEY' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    print("✅ All environment variables are set correctly")
    return True

def test_token_generation():
    """Test verification token generation"""
    print("\n🔍 Testing token generation...")
    
    try:
        token = generate_verification_token()
        if token and len(token) >= 32:
            print(f"✅ Token generated successfully: {token[:8]}...{token[-8:]}")
            return token
        else:
            print("❌ Token generation failed or token too short")
            return None
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return None

def test_verification_email():
    """Test sending verification email"""
    print("\n📧 Testing verification email...")
    
    # Get test email from user
    test_email = input("Enter your email address for testing: ").strip()
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    # Generate test token
    token = generate_verification_token()
    if not token:
        print("❌ Failed to generate token for email test")
        return False
    
    try:
        result = send_verification_email(test_email, token)
        if result:
            print(f"✅ Verification email sent successfully to {test_email}")
            print(f"📝 Verification token: {token}")
            print(f"🔗 Verification URL: {os.getenv('BASE_URL')}/verify-email/{token}")
            return True
        else:
            print("❌ Failed to send verification email")
            return False
    except Exception as e:
        print(f"❌ Error sending verification email: {e}")
        return False

def test_welcome_email():
    """Test sending welcome email"""
    print("\n📧 Testing welcome email...")
    
    # Get test email from user
    test_email = input("Enter your email address for welcome email test (or press Enter to skip): ").strip()
    if not test_email:
        print("⏭️ Skipping welcome email test")
        return True
    
    if '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    try:
        result = send_welcome_email(test_email)
        if result:
            print(f"✅ Welcome email sent successfully to {test_email}")
            return True
        else:
            print("❌ Failed to send welcome email")
            return False
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Brevo Email Verification System Test")
    print("=" * 50)
    
    # Test environment variables
    if not test_environment_variables():
        return False
    
    # Test token generation
    if not test_token_generation():
        return False
    
    # Test verification email
    if not test_verification_email():
        return False
    
    # Test welcome email
    if not test_welcome_email():
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("\n📋 Next steps:")
    print("1. Check your email inbox for the test emails")
    print("2. Verify that the emails look professional and contain correct links")
    print("3. If everything looks good, deploy to Railway with your Brevo credentials")
    print("4. Update Railway environment variables with your Brevo API key")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
