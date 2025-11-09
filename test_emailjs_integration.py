"""
Test script for EmailJS email verification integration
This script tests the email verification functionality using EmailJS
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_utils import send_verification_email, send_welcome_email, generate_verification_token

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test if all required EmailJS environment variables are set"""
    logger.info("Testing EmailJS environment variables...")
    
    required_vars = [
        'EMAILJS_SERVICE_ID',
        'EMAILJS_TEMPLATE_ID',
        'EMAILJS_PUBLIC_KEY',
        'EMAILJS_PRIVATE_KEY',
        'BASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def test_token_generation():
    """Test verification token generation"""
    logger.info("Testing verification token generation...")
    
    token = generate_verification_token()
    
    if not token:
        logger.error("❌ Token generation failed")
        return False
    
    if len(token) < 32:
        logger.error("❌ Token is too short (should be at least 32 characters)")
        return False
    
    logger.info(f"✅ Token generated successfully: {token[:10]}...")
    return True

def test_verification_email():
    """Test sending verification email"""
    logger.info("Testing verification email sending...")
    
    # Use a test email address
    test_email = "test@example.com"
    verification_token = generate_verification_token()
    
    try:
        result = send_verification_email(test_email, verification_token)
        
        if result:
            logger.info("✅ Verification email sent successfully")
            return True
        else:
            logger.error("❌ Verification email sending failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Exception during verification email sending: {str(e)}")
        return False

def test_welcome_email():
    """Test sending welcome email"""
    logger.info("Testing welcome email sending...")
    
    # Use a test email address
    test_email = "test@example.com"
    
    try:
        result = send_welcome_email(test_email)
        
        if result:
            logger.info("✅ Welcome email sent successfully")
            return True
        else:
            logger.error("❌ Welcome email sending failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Exception during welcome email sending: {str(e)}")
        return False

def test_email_configuration():
    """Test EmailJS configuration by checking environment variables"""
    logger.info("Testing EmailJS configuration...")
    
    service_id = os.getenv('EMAILJS_SERVICE_ID')
    template_id = os.getenv('EMAILJS_TEMPLATE_ID')
    public_key = os.getenv('EMAILJS_PUBLIC_KEY')
    private_key = os.getenv('EMAILJS_PRIVATE_KEY')
    base_url = os.getenv('BASE_URL')
    
    logger.info(f"Service ID: {service_id}")
    logger.info(f"Template ID: {template_id}")
    logger.info(f"Public Key: {public_key[:10]}..." if public_key else "Not set")
    logger.info(f"Private Key: {'Set' if private_key else 'Not set'}")
    logger.info(f"Base URL: {base_url}")
    
    # Check if values look correct
    if service_id and service_id.startswith('service_'):
        logger.info("✅ Service ID format looks correct")
    else:
        logger.warning("⚠️ Service ID should start with 'service_'")
    
    if template_id and template_id.startswith('template_'):
        logger.info("✅ Template ID format looks correct")
    else:
        logger.warning("⚠️ Template ID should start with 'template_'")
    
    if public_key and public_key.startswith('user_'):
        logger.info("✅ Public Key format looks correct")
    else:
        logger.warning("⚠️ Public Key should start with 'user_'")
    
    if private_key and private_key.startswith('accessToken_'):
        logger.info("✅ Private Key format looks correct")
    else:
        logger.warning("⚠️ Private Key should start with 'accessToken_'")
    
    return True

def main():
    """Run all tests"""
    logger.info("🧪 Starting EmailJS Integration Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Email Configuration", test_email_configuration),
        ("Token Generation", test_token_generation),
        ("Verification Email", test_verification_email),
        ("Welcome Email", test_welcome_email),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} - PASSED")
            else:
                logger.error(f"❌ {test_name} - FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {str(e)}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! EmailJS integration is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
