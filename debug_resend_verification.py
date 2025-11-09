#!/usr/bin/env python3
"""
Debug script for Resend domain verification issues
This will help identify why verification is stuck on "Pending"
"""

import requests
import os
import json
import time

def check_resend_api_status():
    """Check if Resend API is working"""
    print("🔍 Checking Resend API Status...")
    try:
        response = requests.get("https://api.resend.com/domains", timeout=10)
        if response.status_code == 401:
            print("✅ Resend API is responding (401 = needs auth, which is expected)")
            return True
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Resend API unreachable: {e}")
        return False

def test_resend_domain_verification():
    """Test domain verification with Resend API"""
    api_key = os.getenv('RESEND_API_KEY')
    if not api_key:
        print("❌ RESEND_API_KEY not found in environment")
        return False
    
    print("🔍 Testing Resend Domain Verification...")
    
    # List domains
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get("https://api.resend.com/domains", headers=headers, timeout=10)
        
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Successfully connected to Resend API")
            
            # Find ascendbase.pro domain
            ascendbase_domain = None
            for domain in domains.get('data', []):
                if domain.get('name') == 'ascendbase.pro':
                    ascendbase_domain = domain
                    break
            
            if ascendbase_domain:
                print(f"✅ Found ascendbase.pro domain in Resend")
                print(f"   Status: {ascendbase_domain.get('status', 'unknown')}")
                print(f"   ID: {ascendbase_domain.get('id', 'unknown')}")
                
                # Get detailed domain info
                domain_id = ascendbase_domain.get('id')
                if domain_id:
                    detail_response = requests.get(
                        f"https://api.resend.com/domains/{domain_id}", 
                        headers=headers, 
                        timeout=10
                    )
                    if detail_response.status_code == 200:
                        domain_details = detail_response.json()
                        print("\n📋 Domain Details:")
                        print(json.dumps(domain_details, indent=2))
                        
                        # Check individual record status
                        records = domain_details.get('records', [])
                        for record in records:
                            record_type = record.get('record')
                            status = record.get('status', 'unknown')
                            print(f"   {record_type}: {status}")
                        
                        return domain_details
                    else:
                        print(f"❌ Failed to get domain details: {detail_response.status_code}")
            else:
                print("❌ ascendbase.pro domain not found in Resend")
                print("Available domains:")
                for domain in domains.get('data', []):
                    print(f"   - {domain.get('name', 'unknown')}")
        else:
            print(f"❌ Failed to list domains: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Resend API: {e}")
        return False

def force_domain_verification():
    """Try to force domain verification"""
    api_key = os.getenv('RESEND_API_KEY')
    if not api_key:
        print("❌ RESEND_API_KEY not found")
        return False
    
    print("🔄 Attempting to force domain verification...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # First get domain ID
        response = requests.get("https://api.resend.com/domains", headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get domains: {response.status_code}")
            return False
        
        domains = response.json()
        domain_id = None
        for domain in domains.get('data', []):
            if domain.get('name') == 'ascendbase.pro':
                domain_id = domain.get('id')
                break
        
        if not domain_id:
            print("❌ Domain ID not found")
            return False
        
        # Try to verify domain
        verify_response = requests.post(
            f"https://api.resend.com/domains/{domain_id}/verify",
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            print("✅ Domain verification triggered successfully")
            result = verify_response.json()
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Failed to verify domain: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error forcing verification: {e}")
        return False

def troubleshoot_resend_issues():
    """Comprehensive troubleshooting for Resend verification"""
    print("🔧 Resend Domain Verification Troubleshooting")
    print("=" * 60)
    
    # Check API status
    if not check_resend_api_status():
        print("❌ Resend API is not accessible")
        return
    
    # Test domain verification
    domain_details = test_resend_domain_verification()
    
    if domain_details:
        status = domain_details.get('status', 'unknown')
        if status == 'verified':
            print("🎉 Domain is already verified!")
        elif status == 'pending':
            print("⏳ Domain is still pending verification")
            print("\n🔄 Attempting to force verification...")
            if force_domain_verification():
                print("✅ Verification request sent")
                print("⏳ Wait 2-5 minutes and check Resend dashboard")
            else:
                print("❌ Failed to force verification")
        else:
            print(f"⚠️ Unknown status: {status}")
    
    print("\n📋 Troubleshooting Steps:")
    print("1. Check if DNS records are still correct: python test_domain_verification.py")
    print("2. Try manual verification in Resend dashboard")
    print("3. Contact Resend support if issue persists")
    print("4. Consider removing and re-adding the domain")

def main():
    print("🎭 PSL Morph - Resend Verification Troubleshooter")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    troubleshoot_resend_issues()

if __name__ == "__main__":
    main()
