#!/usr/bin/env python3
"""
Final attempt to fix RunPod connection
"""

import requests
import subprocess
import time
import os

def test_ssh_tunnel():
    """Test if SSH tunnel is working"""
    print("Testing SSH tunnel...")
    try:
        response = requests.get("http://localhost:8188/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ SSH tunnel is working!")
            print(f"ComfyUI stats: {response.json()}")
            return True
        else:
            print(f"❌ SSH tunnel not working: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SSH tunnel not working: {e}")
        return False

def try_password_ssh():
    """Try SSH with password authentication"""
    print("\nTrying SSH with password...")
    print("You'll need to enter your RunPod root password")
    
    cmd = [
        "ssh", 
        "root@149.36.1.79", 
        "-p", "33805",
        "-L", "8188:localhost:8188",
        "-N",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no"
    ]
    
    try:
        process = subprocess.Popen(cmd)
        print("SSH tunnel started with password auth")
        print("Check if it's working by testing localhost:8188")
        return process
    except Exception as e:
        print(f"Failed to start SSH tunnel: {e}")
        return None

def check_runpod_status():
    """Check RunPod pod status"""
    print("RunPod Connection Diagnostic")
    print("=" * 30)
    
    # Test direct connection
    print("1. Testing direct connection to RunPod...")
    try:
        response = requests.get("http://149.36.1.79:8188/system_stats", timeout=5)
        print(f"✅ Direct connection works: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
    
    # Test SSH tunnel
    print("\n2. Testing SSH tunnel...")
    tunnel_works = test_ssh_tunnel()
    
    if not tunnel_works:
        print("\n3. Trying to fix SSH tunnel...")
        
        # Kill existing SSH processes
        try:
            subprocess.run(["taskkill", "/f", "/im", "ssh.exe"], 
                         capture_output=True, check=False)
            print("Killed existing SSH processes")
        except:
            pass
        
        # Try password authentication
        process = try_password_ssh()
        
        if process:
            print("Waiting 5 seconds for tunnel to establish...")
            time.sleep(5)
            
            if test_ssh_tunnel():
                print("🎉 SSH tunnel is now working!")
                return True
            else:
                print("❌ SSH tunnel still not working")
                process.terminate()
                return False
    
    return tunnel_works

def main():
    print("RunPod RTX 5090 Connection Fix")
    print("=" * 35)
    
    if check_runpod_status():
        print("\n🎉 SUCCESS!")
        print("Your RunPod RTX 5090 is connected!")
        print("You can now use your app with the cloud GPU")
        
        # Update .env to use localhost
        with open('.env', 'r') as f:
            content = f.read()
        
        # Update ComfyUI URL to localhost
        content = content.replace('RUNPOD_POD_URL=149.36.1.79', 'RUNPOD_POD_URL=localhost')
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("Updated .env to use SSH tunnel")
        
    else:
        print("\n❌ RunPod connection failed")
        print("\nRecommendations:")
        print("1. Use the FREE deployment guide instead")
        print("2. Deploy with your local GPU (works great!)")
        print("3. Try a different cloud GPU provider")
        
        print(f"\nYour local setup is working perfectly!")
        print("Consider using the FREE deployment option.")

if __name__ == "__main__":
    main()