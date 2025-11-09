#!/usr/bin/env python3
"""
Extract tunnel URL from Cloudflare tunnel window
"""

import win32gui
import win32con
import win32clipboard
import time
import re
import subprocess
import psutil

def find_cloudflare_window():
    """Find the Cloudflare tunnel window"""
    windows = []
    
    def enum_windows_proc(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if 'cloudflare' in window_text.lower() or 'tunnel' in window_text.lower():
                windows.append((hwnd, window_text))
        return True
    
    win32gui.EnumWindows(enum_windows_proc, None)
    return windows

def get_tunnel_url_from_process():
    """Try to get tunnel URL from cloudflared process output"""
    try:
        # Find cloudflared processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                    print(f"Found cloudflared process: PID {proc.info['pid']}")
                    
                    # Try to read from the process (this is tricky on Windows)
                    # Alternative: check if there's a log file or output redirection
                    
                    # For now, let's try a different approach - check netstat for tunnel connections
                    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if ':8188' in line and 'ESTABLISHED' in line:
                            print(f"Found connection to port 8188: {line.strip()}")
                    
                    return None
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    return None

def extract_tunnel_url_from_text(text):
    """Extract tunnel URL from text"""
    patterns = [
        r'https://[a-zA-Z0-9-]+\.trycloudflare\.com',
        r'https://[a-zA-Z0-9-]+\.cloudflareaccess\.com',
        r'Your quick Tunnel: (https://[^\s]+)',
        r'https://[a-zA-Z0-9-]+\.cfargotunnel\.com'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            url = matches[-1]  # Get the latest match
            if isinstance(url, tuple):
                url = url[0]
            return url
    
    return None

def main():
    print("Looking for Cloudflare tunnel URL...")
    
    # Method 1: Try to find from process
    url = get_tunnel_url_from_process()
    if url:
        print(f"Found tunnel URL from process: {url}")
        return url
    
    # Method 2: Try to find Cloudflare window
    windows = find_cloudflare_window()
    if windows:
        print(f"Found {len(windows)} potential Cloudflare windows:")
        for hwnd, title in windows:
            print(f"  - {title}")
    
    # Method 3: Manual instruction
    print("\nCould not automatically detect tunnel URL.")
    print("Please check your Cloudflare tunnel window and look for a line like:")
    print("  https://xxxxx-xxxxx-xxxxx.trycloudflare.com")
    print("\nThen manually register it with:")
    print('  curl -H "Content-Type: application/json" -H "X-TUNNEL-SECRET: morphpas" -d "{\\"url\\":\\"https://your-tunnel-url.trycloudflare.com\\"}" https://psl-morph-production.up.railway.app/register-tunnel')
    
    return None

if __name__ == "__main__":
    main()
