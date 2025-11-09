#!/usr/bin/env python3
"""
Quick verification script for Brevo API credentials
This script checks if your Brevo API key is valid without sending emails
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_brevo_api_key():
    """Verify if the Brevo API key is valid"""
    print("🔍 Verifying Brevo API credentials...")
    
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        print("❌ BREVO_API_KEY not found in environment variables")
        return False
    
    # Mask API key for display
    masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
    print(f"📝 Using API key: {masked_key}")
    
    # Test API key by getting account info
    headers = {
        'accept': 'application/json',
        'api-key': api_key
    }
    
    try:
        print("🌐 Testing API connection...")
        response = requests.get(
            'https://api.brevo.com/v3/account',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account_data = response.json()
            print("✅ API key is valid!")
            print(f"📧 Account email: {account_data.get('email', 'N/A')}")
            print(f"🏢 Company name: {account_data.get('companyName', 'N/A')}")
            
            # Check email sending limits
            plan = account_data.get('plan', [{}])
            if plan:
                plan_info = plan[0] if isinstance(plan, list) else plan
                print(f"📊 Plan type: {plan_info.get('type', 'N/A')}")
                print(f"📈 Credits: {plan_info.get('credits', 'N/A')}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Invalid API key - Authentication failed")
            print("Please check your BREVO_API_KEY in the .env file")
            return False
            
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = {
        'BREVO_API_KEY': 'Your Brevo API key',
        'BREVO_FROM_EMAIL': 'Email address to send from',
        'BREVO_FROM_NAME': 'Name to display as sender',
        'BASE_URL': 'Your app base URL for verification links'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set ({description})")
            all_set = False
    
    return all_set

def main():
    """Main verification function"""
    print("🧪 Brevo API Credentials Verification")
    print("=" * 45)
    
    # Check environment variables
    if not check_environment_variables():
        print("\n❌ Some environment variables are missing.")
        print("Please check your .env file and refer to BREVO_EMAIL_SETUP_GUIDE.md")
        return False
    
    # Verify API key
    if not verify_brevo_api_key():
        print("\n❌ API key verification failed.")
        print("Please check your Brevo API key and try again.")
        return False
    
    print("\n🎉 All credentials verified successfully!")
    print("\n📋 Next steps:")
    print("1. Run 'python test_brevo_email.py' to test email sending")
    print("2. Or run 'test_brevo_email.bat' on Windows")
    print("3. Deploy to Railway with these credentials")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Verification interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
