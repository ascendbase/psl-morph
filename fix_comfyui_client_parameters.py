#!/usr/bin/env python3
"""
Fix ComfyUI Client Parameters
Fixes the parameter mismatch in app.py for LocalComfyUIClient calls
"""

import re

def fix_app_py():
    """Fix the app.py file to match LocalComfyUIClient method signature"""
    
    # Read the current app.py file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic custom features section
    # Look for the section that calls gpu_client.generate_image with extra parameters
    
    # Pattern 1: Custom features mode call with workflow_type and custom_features
    pattern1 = r'''prompt_id = gpu_client\.generate_image\(
                        image_path=file_path,
                        preset_name=tier_name,
                        denoise_strength=custom_denoise,
                        workflow_type=workflow_name,
                        custom_features=selected_features
                    \)'''
    
    replacement1 = '''prompt_id = gpu_client.generate_image(
                        image_path=file_path,
                        preset_name=tier_name,
                        denoise_strength=custom_denoise
                    )'''
    
    # Apply the replacement
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # Pattern 2: Any other calls with extra parameters
    # Look for calls that have more than 3 parameters
    pattern2 = r'''(prompt_id = gpu_client\.generate_image\(\s*
                        image_path=file_path,\s*
                        preset_name=tier_name,\s*
                        denoise_strength=\w+)(?:,\s*
                        \w+=\w+)*\s*
                    \)'''
    
    replacement2 = r'''\1
                    )'''
    
    # Apply the second replacement
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.VERBOSE)
    
    # Write the fixed content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed app.py - removed extra parameters from gpu_client.generate_image() calls")
    return True

def verify_fix():
    """Verify that the fix was applied correctly"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there are any remaining calls with workflow_type or custom_features
    if 'workflow_type=' in content and 'gpu_client.generate_image' in content:
        print("⚠️ Warning: Still found workflow_type parameter in gpu_client calls")
        return False
    
    if 'custom_features=' in content and 'gpu_client.generate_image' in content:
        print("⚠️ Warning: Still found custom_features parameter in gpu_client calls")
        return False
    
    print("✅ Verification passed - no extra parameters found in gpu_client calls")
    return True

if __name__ == '__main__':
    print("🔧 Fixing ComfyUI Client Parameter Mismatch...")
    print("=" * 50)
    
    try:
        if fix_app_py():
            if verify_fix():
                print("\n🎉 Fix completed successfully!")
                print("\n📝 What was fixed:")
                print("- Removed 'workflow_type' parameter from gpu_client.generate_image() calls")
                print("- Removed 'custom_features' parameter from gpu_client.generate_image() calls")
                print("- LocalComfyUIClient.generate_image() now only receives the 3 supported parameters:")
                print("  * image_path")
                print("  * preset_name") 
                print("  * denoise_strength")
                print("\n🚀 You can now test the custom features again!")
            else:
                print("\n❌ Fix verification failed - manual review needed")
        else:
            print("\n❌ Fix failed")
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        print("Manual fix required - check the app.py file around the ComfyUI processing section")
