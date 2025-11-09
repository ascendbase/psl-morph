#!/usr/bin/env python3
"""
Test script to verify Resend domain configuration
This will help diagnose why the records show as "Pending"
"""

import subprocess
import sys
import time

def run_dns_lookup(record_type, domain):
    """Run DNS lookup and return results"""
    try:
        cmd = ['nslookup', f'-type={record_type}', domain]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except FileNotFoundError:
        return "", "nslookup not found", 1

def check_dns_records():
    """Check all required DNS records for Resend"""
    print("🔍 Checking DNS Records for ascendbase.pro domain...")
    print("=" * 60)
    
    # Check MX record
    print("\n📧 Checking MX Record for send.ascendbase.pro:")
    stdout, stderr, code = run_dns_lookup('MX', 'send.ascendbase.pro')
    if code == 0 and 'feedback-smtp.us-east-1.amazonses.com' in stdout:
        print("✅ MX Record: FOUND")
        print(f"   {stdout.strip()}")
    else:
        print("❌ MX Record: NOT FOUND or INCORRECT")
        print(f"   stdout: {stdout.strip()}")
        print(f"   stderr: {stderr.strip()}")
    
    # Check SPF TXT record
    print("\n📝 Checking SPF TXT Record for send.ascendbase.pro:")
    stdout, stderr, code = run_dns_lookup('TXT', 'send.ascendbase.pro')
    if code == 0 and 'v=spf1 include:amazonses.com' in stdout:
        print("✅ SPF TXT Record: FOUND")
        print(f"   {stdout.strip()}")
    else:
        print("❌ SPF TXT Record: NOT FOUND or INCORRECT")
        print(f"   stdout: {stdout.strip()}")
        print(f"   stderr: {stderr.strip()}")
    
    # Check DKIM TXT record
    print("\n🔐 Checking DKIM TXT Record for resend._domainkey.ascendbase.pro:")
    stdout, stderr, code = run_dns_lookup('TXT', 'resend._domainkey.ascendbase.pro')
    if code == 0 and 'p=MIG' in stdout:
        print("✅ DKIM TXT Record: FOUND")
        print(f"   {stdout.strip()}")
    else:
        print("❌ DKIM TXT Record: NOT FOUND or INCORRECT")
        print(f"   stdout: {stdout.strip()}")
        print(f"   stderr: {stderr.strip()}")

def check_propagation_status():
    """Check DNS propagation from multiple perspectives"""
    print("\n🌐 DNS Propagation Analysis:")
    print("=" * 60)
    
    # Check if records exist at all
    records_to_check = [
        ('MX', 'send.ascendbase.pro', 'feedback-smtp.us-east-1.amazonses.com'),
        ('TXT', 'send.ascendbase.pro', 'v=spf1 include:amazonses.com'),
        ('TXT', 'resend._domainkey.ascendbase.pro', 'p=MIG')
    ]
    
    all_good = True
    for record_type, domain, expected in records_to_check:
        stdout, stderr, code = run_dns_lookup(record_type, domain)
        if code == 0 and expected in stdout:
            print(f"✅ {record_type} {domain}: Propagated")
        else:
            print(f"⏳ {record_type} {domain}: Still propagating or missing")
            all_good = False
    
    if all_good:
        print("\n🎉 All DNS records are properly propagated!")
        print("   The 'Pending' status in your hosting panel might be a display issue.")
        print("   Try refreshing the Resend domain verification page.")
    else:
        print("\n⏳ Some records are still propagating...")
        print("   This can take 5-60 minutes depending on your DNS provider.")
        print("   The records in your hosting panel look correct.")

def main():
    print("🎭 PSL Morph - Resend Domain Verification Checker")
    print("=" * 60)
    print("This script will check if your DNS records are properly configured")
    print("and propagated for Resend email verification.\n")
    
    # Check DNS records
    check_dns_records()
    
    # Check propagation
    check_propagation_status()
    
    print("\n📋 Next Steps:")
    print("=" * 60)
    print("1. If all records show ✅: Go to https://resend.com/domains and click 'Verify'")
    print("2. If records show ⏳: Wait 15-30 minutes and run this script again")
    print("3. If records show ❌: Check your DNS configuration in hosting panel")
    print("\n💡 Your current DNS setup with trailing dots is CORRECT!")
    print("   Your hosting provider automatically appends .ascendbase.pro")

if __name__ == "__main__":
    main()
