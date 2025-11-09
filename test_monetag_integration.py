#!/usr/bin/env python3
"""
Test script to verify Monetag integration is properly implemented
"""

import os
import re
from pathlib import Path

def test_sw_js_exists():
    """Test that sw.js file exists in root directory"""
    sw_path = Path("sw.js")
    if sw_path.exists():
        print("✅ sw.js file exists in root directory")
        return True
    else:
        print("❌ sw.js file NOT found in root directory")
        return False

def test_sw_js_content():
    """Test that sw.js contains Monetag service worker code"""
    try:
        with open("sw.js", "r") as f:
            content = f.read()
        
        # Check for obfuscated Monetag patterns
        if "grookilteepsou.net" in content and "9790545" in content:
            print("✅ sw.js contains Monetag service worker code")
            return True
        else:
            print("❌ sw.js does not contain expected Monetag code")
            return False
    except Exception as e:
        print(f"❌ Error reading sw.js: {e}")
        return False

def test_flask_route():
    """Test that Flask app.py has the sw.js serving route"""
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Check for the sw.js route
        if "@app.route('/sw.js')" in content and "def serve_sw():" in content:
            print("✅ Flask app has sw.js serving route")
            return True
        else:
            print("❌ Flask app missing sw.js serving route")
            return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_monetag_script_in_templates():
    """Test that Monetag script is integrated in HTML templates"""
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return False
    
    # Files that should have Monetag script
    test_files = [
        "index.html",
        "dashboard.html", 
        "auth/login.html",
        "auth/register.html",
        "auth/profile.html",
        "facial_evaluation/dashboard.html",
        "payments/buy_credits.html",
        "payments/payment_success.html",
        "ratios_morph/dashboard.html"
    ]
    
    monetag_script = 'src="https://fpyf8.com/88/tag.min.js" data-zone="167059"'
    service_worker_registration = "navigator.serviceWorker.register('/sw.js')"
    
    results = []
    
    for file_path in test_files:
        full_path = templates_dir / file_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                has_monetag = monetag_script in content
                has_sw_registration = service_worker_registration in content
                
                if has_monetag and has_sw_registration:
                    print(f"✅ {file_path}: Monetag script + service worker registration")
                    results.append(True)
                elif has_monetag:
                    print(f"⚠️  {file_path}: Has Monetag script but missing service worker registration")
                    results.append(False)
                else:
                    print(f"❌ {file_path}: Missing Monetag script")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                results.append(False)
        else:
            print(f"⚠️  {file_path}: File not found")
            results.append(False)
    
    return all(results)

def test_admin_templates_excluded():
    """Test that admin templates do NOT have Monetag script (as requested)"""
    templates_dir = Path("templates")
    admin_files = [
        "admin/dashboard.html",
        "admin/facial_evaluations.html",
        "admin/respond_facial_evaluation.html",
        "admin/ratios_morphs.html",
        "admin/respond_ratios_morph.html"
    ]
    
    monetag_script = 'src="https://fpyf8.com/88/tag.min.js"'
    
    results = []
    
    for file_path in admin_files:
        full_path = templates_dir / file_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if monetag_script not in content:
                    print(f"✅ {file_path}: Correctly excluded from Monetag")
                    results.append(True)
                else:
                    print(f"❌ {file_path}: Unexpectedly contains Monetag script")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                results.append(False)
        else:
            print(f"⚠️  {file_path}: File not found")
            results.append(True)  # Not found is OK for admin exclusion test
    
    return all(results)

def main():
    """Run all Monetag integration tests"""
    print("🔍 Testing Monetag Integration")
    print("=" * 50)
    
    tests = [
        ("SW.js File Exists", test_sw_js_exists),
        ("SW.js Content Valid", test_sw_js_content),
        ("Flask Route Present", test_flask_route),
        ("Templates Have Monetag", test_monetag_script_in_templates),
        ("Admin Templates Excluded", test_admin_templates_excluded)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ Monetag integration is properly implemented!")
        print("\n📝 Integration includes:")
        print("   • Monetag script tag in all non-admin pages")
        print("   • Service worker (sw.js) properly placed and served")
        print("   • Service worker registration in all pages")
        print("   • Admin pages correctly excluded")
        print("\n🚀 Your app is ready for Monetag monetization!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("\n🔧 Please review the failed tests above and fix any issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
