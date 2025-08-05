#!/usr/bin/env python3
"""
SSH Tunnel Setup for RunPod ComfyUI Access
Creates an SSH tunnel to access ComfyUI through the exposed SSH port
"""

import subprocess
import sys
import time
import requests
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SSHTunnel:
    def __init__(self):
        self.pod_ip = "149.36.1.79"
        self.ssh_port = "33805"
        self.local_port = "8188"
        self.remote_port = "8188"
        self.tunnel_process = None
        
    def create_tunnel(self):
        """Create SSH tunnel to ComfyUI"""
        print("Setting up SSH tunnel to RunPod...")
        print(f"Tunnel: localhost:{self.local_port} -> {self.pod_ip}:{self.remote_port}")
        
        # SSH tunnel command
        ssh_cmd = [
            "ssh",
            "-L", f"{self.local_port}:localhost:{self.remote_port}",
            "-p", self.ssh_port,
            f"root@{self.pod_ip}",
            "-N",  # Don't execute remote command
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR"
        ]
        
        try:
            print("Starting SSH tunnel...")
            print("Note: You may need to enter your SSH password/key")
            
            # Start the tunnel in background
            self.tunnel_process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for tunnel to establish
            time.sleep(3)
            
            # Test if tunnel is working
            if self.test_tunnel():
                print("✅ SSH tunnel established successfully!")
                print(f"ComfyUI is now accessible at: http://localhost:{self.local_port}")
                return True
            else:
                print("❌ SSH tunnel failed to establish")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create SSH tunnel: {e}")
            return False
    
    def test_tunnel(self):
        """Test if the SSH tunnel is working"""
        try:
            response = requests.get(f"http://localhost:{self.local_port}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def close_tunnel(self):
        """Close the SSH tunnel"""
        if self.tunnel_process:
            self.tunnel_process.terminate()
            print("SSH tunnel closed")

def update_env_for_tunnel():
    """Update .env file to use localhost tunnel"""
    env_content = """# Face Morphing App - SSH Tunnel Configuration
# Using SSH tunnel to access RunPod ComfyUI

# =============================================================================
# SSH TUNNEL CONFIGURATION
# =============================================================================

# Use localhost through SSH tunnel
USE_CLOUD_GPU=true
USE_RUNPOD_POD=true
RUNPOD_POD_URL=localhost
RUNPOD_POD_PORT=8188

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Environment
ENVIRONMENT=production

# Flask Configuration
SECRET_KEY=your_very_secure_secret_key_here_change_this
DEBUG=false
HOST=0.0.0.0
PORT=5000

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DATABASE_URL=sqlite:///face_morph.db

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================

LOGIN_DISABLED=false
SECURE_FILENAME_ENABLED=true
MAX_CONTENT_LENGTH=16777216

# =============================================================================
# PAYMENT PROCESSING (for Kyrgyzstan)
# =============================================================================

CRYPTO_WALLET_BTC=your_btc_wallet_address
CRYPTO_WALLET_ETH=your_eth_wallet_address
CRYPTO_WALLET_USDT=your_usdt_wallet_address

BANK_NAME=Your Bank Name
BANK_ACCOUNT=Your Account Number
BANK_ROUTING=Your Routing Number

# =============================================================================
# LOGGING & MONITORING
# =============================================================================

LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# =============================================================================
# LEGACY SETTINGS
# =============================================================================

COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_TIMEOUT=300
CURRENT_WORKFLOW=facedetailer
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file for SSH tunnel configuration")

def main():
    print("RunPod SSH Tunnel Setup")
    print("=" * 40)
    
    # Create tunnel
    tunnel = SSHTunnel()
    
    if tunnel.create_tunnel():
        # Update .env file
        update_env_for_tunnel()
        
        print("\n🎉 Setup Complete!")
        print("=" * 40)
        print("1. SSH tunnel is running")
        print("2. .env file updated")
        print("3. ComfyUI accessible at http://localhost:8188")
        print("4. You can now run: python app.py")
        print("\nPress Ctrl+C to stop the tunnel")
        
        try:
            # Keep tunnel alive
            while True:
                if not tunnel.test_tunnel():
                    print("❌ Tunnel connection lost, attempting to reconnect...")
                    tunnel.close_tunnel()
                    time.sleep(2)
                    tunnel.create_tunnel()
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nShutting down...")
            tunnel.close_tunnel()
    else:
        print("❌ Failed to establish SSH tunnel")
        print("\nTroubleshooting:")
        print("1. Make sure your RunPod is running")
        print("2. Verify SSH access: ssh root@149.36.1.79 -p 33805")
        print("3. Ensure ComfyUI is running on the pod: python main.py --listen 0.0.0.0 --port 8188")

if __name__ == "__main__":
    main()