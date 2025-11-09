#!/usr/bin/env python3
"""
Real-time Active Cloudflare Tunnel Detection
This script actually detects the REAL running tunnel URL from cloudflared logs
"""

import subprocess
import re
import requests
import time
import os
import json
from typing import Optional

def get_cloudflared_log_output() -> Optional[str]:
    """Get the current output from running cloudflared process"""
    try:
        # Method 1: Try to find cloudflared process and get its output
        result = subprocess.run(
            ['wmic', 'process', 'where', 'name="cloudflared.exe"', 'get', 'commandline', '/format:list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if 'cloudflared.exe' in result.stdout:
            print("✅ Found running cloudflared process")
            
            # Method 2: Check if there's a log file
            possible_log_paths = [
                'cloudflared.log',
                'tunnel.log',
                os.path.expanduser('~/.cloudflared/tunnel.log'),
                'C:\\Users\\%USERNAME%\\.cloudflared\\tunnel.log'
            ]
            
            for log_path in possible_log_paths:
                if os.path.exists(log_path):
                    print(f"📄 Found log file: {log_path}")
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
            
            # Method 3: Try to capture live output from cloudflared
            print("🔍 Attempting to capture live cloudflared output...")
            try:
                # Start a new quick tunnel to see the output
                result = subprocess.run(
                    ['cloudflared', 'tunnel', '--url', 'http://127.0.0.1:8188'],
                    capture_output=True,
                    text=True,
                    timeout=15  # Give it 15 seconds to start
                )
                return result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                print("⏰ Timeout waiting for cloudflared output")
                return None
                
    except Exception as e:
        print(f"❌ Error getting cloudflared output: {e}")
        return None

def extract_tunnel_url_from_output(output: str) -> Optional[str]:
    """Extract tunnel URL from cloudflared output"""
    if not output:
        return None
    
    # Common patterns for tunnel URLs in cloudflared output
    patterns = [
        r'https://[\w-]+\.trycloudflare\.com',
        r'https://[\w-]+\.cloudflareaccess\.com',
        r'https://[\w-]+\.cfargotunnel\.com',
        r'Your quick Tunnel has been created! Visit it at \(Ctrl\+C to quit\):\s*(https://[\w-]+\.trycloudflare\.com)',
        r'Visit it at.*?(https://[\w-]+\.trycloudflare\.com)',
        r'Tunnel.*?(https://[\w-]+\.trycloudflare\.com)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            # Return the first valid match
            for match in matches:
                url = match if match.startswith('https://') else match
                print(f"🎯 Found tunnel URL in output: {url}")
                return url
    
    print("❌ No tunnel URL found in output")
    return None

def test_tunnel_url(url: str) -> bool:
    """Test if the tunnel URL actually works with ComfyUI"""
    try:
        print(f"🧪 Testing tunnel URL: {url}")
        response = requests.get(f"{url}/system_stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'system' in data and 'comfyui_version' in data.get('system', {}):
                print(f"✅ Tunnel is working! ComfyUI version: {data['system']['comfyui_version']}")
                return True
            else:
                print("❌ URL responds but it's not ComfyUI")
                return False
        else:
            print(f"❌ URL returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tunnel URL: {e}")
        return False

def scan_for_active_tunnel() -> Optional[str]:
    """Scan for currently active Cloudflare tunnel"""
    print("🔍 Scanning for active Cloudflare tunnel...")
    
    # Method 1: Try to get tunnel URL from cloudflared output
    output = get_cloudflared_log_output()
    if output:
        url = extract_tunnel_url_from_output(output)
        if url and test_tunnel_url(url):
            return url
    
    # Method 2: Check if there's a tunnel info file
    tunnel_info_paths = [
        'tunnel_info.json',
        'current_tunnel.txt',
        '.tunnel_url'
    ]
    
    for path in tunnel_info_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if content.startswith('https://') and 'trycloudflare.com' in content:
                        if test_tunnel_url(content):
                            print(f"✅ Found working tunnel from {path}: {content}")
                            return content
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
    
    # Method 3: Try to start a new tunnel and capture its URL
    print("🚀 No existing tunnel found, attempting to start new tunnel...")
    try:
        # Start cloudflared in background and capture output
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://127.0.0.1:8188'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for tunnel to start and capture output
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < 30:  # Wait up to 30 seconds
            line = process.stdout.readline()
            if line:
                output_lines.append(line)
                print(f"📝 Cloudflared: {line.strip()}")
                
                # Check if we found a tunnel URL
                url = extract_tunnel_url_from_output(line)
                if url:
                    # Test the URL
                    time.sleep(2)  # Give tunnel a moment to fully start
                    if test_tunnel_url(url):
                        # Save the tunnel URL for future use
                        with open('current_tunnel.txt', 'w') as f:
                            f.write(url)
                        print(f"💾 Saved tunnel URL to current_tunnel.txt")
                        return url
            
            # Check if process has terminated
            if process.poll() is not None:
                break
                
            time.sleep(0.5)
        
        # Clean up process
        process.terminate()
        
    except Exception as e:
        print(f"❌ Error starting new tunnel: {e}")
    
    print("❌ Could not detect or start active tunnel")
    return None

def main():
    """Main function to detect active tunnel"""
    print("🚀 Active Cloudflare Tunnel Detection")
    print("=" * 50)
    
    # First check if ComfyUI is running locally
    try:
        response = requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI is running locally on port 8188")
        else:
            print("❌ ComfyUI is not responding on port 8188")
            print("Please start ComfyUI first!")
            return None
    except:
        print("❌ ComfyUI is not running on port 8188")
        print("Please start ComfyUI first!")
        return None
    
    # Now scan for active tunnel
    tunnel_url = scan_for_active_tunnel()
    
    if tunnel_url:
        print("\n" + "=" * 50)
        print("🎉 SUCCESS!")
        print(f"Active tunnel URL: {tunnel_url}")
        print("=" * 50)
        
        # Save to registry
        try:
            import sys
            sys.path.append('.')
            from tunnel_registry import set_tunnel_url
            set_tunnel_url(tunnel_url)
            print("💾 Saved tunnel URL to registry")
        except Exception as e:
            print(f"⚠️ Could not save to registry: {e}")
        
        return tunnel_url
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED!")
        print("Could not detect or start active tunnel")
        print("=" * 50)
        return None

if __name__ == "__main__":
    main()
