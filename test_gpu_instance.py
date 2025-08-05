#!/usr/bin/env python3
"""
Test connection to your new GPU instance
"""

import requests
import os
from dotenv import load_dotenv

def test_gpu_instance(ip_address):
    """Test connection to GPU instance"""
    
    print(f"Testing GPU Instance Connection")
    print("=" * 40)
    print(f"IP Address: {ip_address}")
    print(f"Port: 8188")
    print()
    
    # Test URLs
    base_url = f"http://{ip_address}:8188"
    test_urls = [
        f"{base_url}/system_stats",
        f"{base_url}/queue",
        f"{base_url}/history",
        base_url  # Main ComfyUI interface
    ]
    
    print("Testing endpoints...")
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}")
                if 'system_stats' in url:
                    try:
                        stats = response.json()
                        print(f"   GPU Info: {stats}")
                    except:
                        print("   Response received but not JSON")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED: Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ FAILED: Timeout")
        except Exception as e:
            print(f"❌ FAILED: {e}")
        
        print()
    
    # Test if we can update .env
    print("Configuration Update:")
    print(f"Add this to your .env file:")
    print(f"COMFYUI_URL=http://{ip_address}:8188")
    print()
    
    return base_url

def update_env_file(ip_address):
    """Update .env file with new GPU instance"""
    
    # Read current .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update ComfyUI URL
    new_url = f"http://{ip_address}:8188"
    
    if 'COMFYUI_URL=' in env_content:
        # Replace existing URL
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('COMFYUI_URL='):
                lines[i] = f"COMFYUI_URL={new_url}"
        env_content = '\n'.join(lines)
    else:
        # Add new URL
        env_content += f"\nCOMFYUI_URL={new_url}\n"
    
    # Also ensure cloud GPU is disabled
    if 'USE_CLOUD_GPU=' not in env_content:
        env_content += "USE_CLOUD_GPU=false\n"
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Updated .env file with GPU instance: {new_url}")

def main():
    print("GPU Instance Connection Tester")
    print("=" * 35)
    
    # Get IP address from user
    ip_address = input("Enter your GPU instance IP address: ").strip()
    
    if not ip_address:
        print("❌ No IP address provided")
        return
    
    print()
    
    # Test connection
    base_url = test_gpu_instance(ip_address)
    
    # Ask if user wants to update .env
    update = input("Update .env file with this GPU instance? (y/n): ").strip().lower()
    
    if update == 'y':
        update_env_file(ip_address)
        print()
        print("🎉 Configuration updated!")
        print("Now restart your app:")
        print("1. Stop current app (Ctrl+C)")
        print("2. Run: python app.py")
        print("3. Test image generation")
    else:
        print("Configuration not updated.")
        print(f"Manual update: COMFYUI_URL=http://{ip_address}:8188")

if __name__ == "__main__":
    main()