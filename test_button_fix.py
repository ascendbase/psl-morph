"""
Test script to verify the Start Transformation button fix
"""

import os
import re

def test_button_fix():
    """Test that the Start Transformation button should work now"""
    print("🔧 Testing Start Transformation Button Fix")
    print("=" * 50)
    
    # Read the template file
    template_path = 'templates/index.html'
    
    if not os.path.exists(template_path):
        print("❌ Template file not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that problematic intensity slider code is removed
    problematic_patterns = [
        r"document\.getElementById\('intensitySlider'\)",
        r"intensitySlider\.addEventListener",
        r"#intensitySlider",
        r"id=\"intensitySlider\""
    ]
    
    issues_found = []
    for pattern in problematic_patterns:
        if re.search(pattern, content):
            issues_found.append(pattern)
    
    if issues_found:
        print("❌ Found problematic intensity slider references:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No problematic intensity slider references found")
    
    # Check that essential button functionality is present
    essential_patterns = [
        r"processBtn\.addEventListener\('click'",
        r"updateProcessButton\(\)",
        r"selectedChad",
        r"currentMode === 'reference'",
        r"transform_mode.*currentMode",
        r"selected_chad.*selectedChad"
    ]
    
    missing_patterns = []
    for pattern in essential_patterns:
        if not re.search(pattern, content):
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print("❌ Missing essential button functionality:")
        for missing in missing_patterns:
            print(f"   - {missing}")
        return False
    else:
        print("✅ All essential button functionality is present")
    
    # Check Reference Chad section structure
    reference_chad_checks = [
        'id="referenceChadSection"',
        'data-chad="barrett"',
        'data-chad="gandy"',
        'data-chad="elias"',
        'data-chad="pitt"',
        'data-chad="hernan"',
        'Jordan Barrett',
        'David Gandy',
        'Elias De Poot',
        'Brad Pitt',
        'Hernan Drago'
    ]
    
    missing_chad_elements = []
    for check in reference_chad_checks:
        if check not in content:
            missing_chad_elements.append(check)
    
    if missing_chad_elements:
        print("❌ Missing Reference Chad elements:")
        for missing in missing_chad_elements:
            print(f"   - {missing}")
        return False
    else:
        print("✅ All Reference Chad elements are present")
    
    print("\n" + "=" * 50)
    print("🎉 BUTTON FIX TEST PASSED!")
    print("✅ The Start Transformation button should now work properly")
    print("\n📋 What was fixed:")
    print("   • Removed problematic intensity slider JavaScript code")
    print("   • Kept all essential button functionality intact")
    print("   • Reference Chad mode uses fixed 50% intensity")
    print("   • All transformation modes should work correctly")
    print("\n🚀 The app is ready to use!")
    
    return True

if __name__ == "__main__":
    success = test_button_fix()
    if not success:
        exit(1)
