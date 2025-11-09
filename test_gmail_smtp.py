"""
Test script for Gmail SMTP email verification system
This script tests the email sending functionality using Gmail SMTP
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_utils import generate_verification_token, send_verification_email, send_welcome_email

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = ['GMAIL_EMAIL', 'GMAIL_APP_PASSWORD', 'BASE_URL']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)}")  # Hide actual values
    
    if missing_vars:
        print(f"❌ Missing or placeholder environment variables: {', '.join(missing_vars)}")
        print("\nPlease update your .env file with actual values:")
        for var in missing_vars:
            if var == 'GMAIL_EMAIL':
                print(f"   {var}=your_actual_email@gmail.com")
            elif var == 'GMAIL_APP_PASSWORD':
                print(f"   {var}=your_16_character_app_password")
            elif var == 'BASE_URL':
                print(f"   {var}=https://your-app-name.up.railway.app")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_token_generation():
    """Test verification token generation"""
    print("\n🔍 Testing Token Generation...")
    
    try:
        token = generate_verification_token()
        if token and len(token) > 20:  # Should be a long secure token
            print(f"✅ Token generated successfully: {token[:10]}...")
            return token
        else:
            print("❌ Token generation failed or token too short")
            return None
    except Exception as e:
        print(f"❌ Token generation error: {str(e)}")
        return None

def test_verification_email(test_email, token):
    """Test sending verification email"""
    print(f"\n🔍 Testing Verification Email to {test_email}...")
    
    try:
        success = send_verification_email(test_email, token)
        if success:
            print("✅ Verification email sent successfully!")
            print(f"📧 Check your inbox at {test_email}")
            print("📧 Check spam folder if not found in inbox")
            return True
        else:
            print("❌ Failed to send verification email")
            return False
    except Exception as e:
        print(f"❌ Verification email error: {str(e)}")
        return False

def test_welcome_email(test_email):
    """Test sending welcome email"""
    print(f"\n🔍 Testing Welcome Email to {test_email}...")
    
    try:
        success = send_welcome_email(test_email)
        if success:
            print("✅ Welcome email sent successfully!")
            print(f"📧 Check your inbox at {test_email}")
            return True
        else:
            print("❌ Failed to send welcome email")
            return False
    except Exception as e:
        print(f"❌ Welcome email error: {str(e)}")
        return False

def get_test_email():
    """Get test email from user input"""
    gmail_email = os.getenv('GMAIL_EMAIL')
    
    print(f"\n📧 Enter test email address (or press Enter to use {gmail_email}):")
    test_email = input().strip()
    
    if not test_email:
        test_email = gmail_email
    
    return test_email

def main():
    """Main test function"""
    print("🚀 Gmail SMTP Email Verification Test")
    print("=" * 50)
    
    # Test 1: Environment Variables
    if not test_environment_variables():
        print("\n❌ Environment setup failed. Please fix the issues above and try again.")
        return
    
    # Test 2: Token Generation
    token = test_token_generation()
    if not token:
        print("\n❌ Token generation failed. Cannot proceed with email tests.")
        return
    
    # Get test email
    test_email = get_test_email()
    if not test_email:
        print("❌ No test email provided")
        return
    
    print(f"\n📧 Using test email: {test_email}")
    
    # Test 3: Verification Email
    verification_success = test_verification_email(test_email, token)
    
    # Test 4: Welcome Email
    welcome_success = test_welcome_email(test_email)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", True),
        ("Token Generation", token is not None),
        ("Verification Email", verification_success),
        ("Welcome Email", welcome_success)
    ]
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in tests)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Gmail SMTP setup is working correctly.")
        print("\n📋 Next steps:")
        print("1. Update your Railway environment variables with the same Gmail credentials")
        print("2. Deploy your application to Railway")
        print("3. Test registration on your live application")
    else:
        print("\n❌ Some tests failed. Please check the errors above and:")
        print("1. Verify your Gmail App Password is correct")
        print("2. Ensure 2-Step Verification is enabled on your Gmail account")
        print("3. Check your internet connection")
        print("4. Try regenerating your Gmail App Password")

if __name__ == "__main__":
    main()
