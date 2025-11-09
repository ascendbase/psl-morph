#!/usr/bin/env python3
"""
Automatic Cloudflare Tunnel Detection for ComfyUI
This module automatically detects running Cloudflare tunnels and updates the configuration
"""

import requests
import json
import re
import subprocess
import time
import logging
import os
from typing import Optional, List, Dict
from tunnel_registry import get_tunnel_url

logger = logging.getLogger(__name__)

class CloudflareTunnelDetector:
    """Automatically detect and connect to Cloudflare tunnels"""
    
    def __init__(self):
        self.detected_url = None
        self.last_check = 0
        self.check_interval = 30  # Check every 30 seconds
        self.known_patterns = [
            r'https://[\w-]+\.trycloudflare\.com',
            r'https://[\w-]+\.cloudflareaccess\.com',
            r'https://[\w-]+\.cfargotunnel\.com'
        ]
    
    def detect_tunnel_from_logs(self) -> Optional[str]:
        """Detect tunnel URL from running cloudflared process logs"""
        try:
            # Import and use the real tunnel detection
            from detect_active_tunnel import scan_for_active_tunnel
            logger.info("Using real-time tunnel detection...")
            return scan_for_active_tunnel()
            
        except Exception as e:
            logger.debug(f"Real-time detection failed, falling back to process detection: {e}")
            
            # Fallback to basic process detection
            try:
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq cloudflared.exe', '/FO', 'CSV'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if 'cloudflared.exe' in result.stdout:
                    logger.info("Found running cloudflared process")
                    
                    # Check for saved tunnel URL
                    tunnel_files = ['current_tunnel.txt', 'tunnel_info.json', '.tunnel_url']
                    for file_path in tunnel_files:
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, 'r') as f:
                                    url = f.read().strip()
                                    if url.startswith('https://') and 'trycloudflare.com' in url:
                                        if self._test_comfyui_connection(url):
                                            logger.info(f"Found working tunnel from {file_path}: {url}")
                                            return url
                            except Exception as e:
                                logger.debug(f"Error reading {file_path}: {e}")
                
            except Exception as e:
                logger.debug(f"Process detection failed: {e}")
        
        return None
    
    def _scan_for_tunnel_urls(self) -> Optional[str]:
        """Scan common tunnel URL patterns"""
        # Try some common tunnel URL patterns
        common_prefixes = [
            'keeping-za-volume-enclosed',  # Current tunnel
            'statute-pas-org-southeast',
            'quick-tunnel',
            'tunnel',
            'comfyui',
            'morph'
        ]
        
        # Also try some random pattern scanning
        import random
        import string
        
        # First try known patterns
        for prefix in common_prefixes:
            test_url = f"https://{prefix}.trycloudflare.com"
            if self._test_comfyui_connection(test_url):
                logger.info(f"Found working tunnel: {test_url}")
                return test_url
        
        # Try to scan for active tunnels by checking common patterns
        tunnel_patterns = [
            'keeping-za-volume-enclosed',
            'halloween-fitted-common-slovakia',
            'statute-pas-org-southeast'
        ]
        
        for pattern in tunnel_patterns:
            test_url = f"https://{pattern}.trycloudflare.com"
            if self._test_comfyui_connection(test_url):
                logger.info(f"Found working tunnel: {test_url}")
                return test_url
        
        return None
    
    def _test_comfyui_connection(self, url: str) -> bool:
        """Test if URL is a working ComfyUI instance"""
        try:
            response = requests.get(f"{url}/system_stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Check if it's actually ComfyUI
                if 'system' in data and 'comfyui_version' in data.get('system', {}):
                    return True
        except:
            pass
        return False
    
    def detect_tunnel_url(self) -> Optional[str]:
        """Main method to detect tunnel URL
        
        Strategy (in order):
         1. Respect a persisted registry URL (written by start scripts) if present and responding
         2. Try to detect cloudflared from local processes/logs (only works when running on same host)
         3. Use quick pattern scanning as a last resort
        """
        current_time = time.time()
        
        # Rate limit checks
        if current_time - self.last_check < self.check_interval:
            return self.detected_url
        
        self.last_check = current_time
        
        # 1) Check persisted registry if available (useful when start scripts register the quick URL)
        try:
            reg_url = get_tunnel_url()
            if reg_url:
                logger.debug(f"Found registered tunnel URL: {reg_url} - testing connectivity")
                if self._test_comfyui_connection(reg_url):
                    logger.info(f"Registered tunnel is reachable: {reg_url}")
                    self.detected_url = reg_url
                    return reg_url
                else:
                    logger.debug("Registered tunnel not responding")
        except Exception as e:
            logger.debug(f"Registry check failed: {e}")
        
        # 2) Try to detect from running processes/logs (works when cloudflared runs on same host)
        url = self.detect_tunnel_from_logs()
        if url:
            self.detected_url = url
            return url
        
        # 3) If we already have a previously-detected URL, validate it
        if self.detected_url and self._test_comfyui_connection(self.detected_url):
            return self.detected_url
        
        # 4) Scan for common/likely trycloudflare patterns (last resort)
        url = self._scan_for_tunnel_urls()
        if url:
            self.detected_url = url
            return url
        
        logger.debug("No Cloudflare tunnel detected")
        return None
    
    def get_tunnel_info(self) -> Dict:
        """Get detailed tunnel information"""
        url = self.detect_tunnel_url()
        if not url:
            return {
                'status': 'not_found',
                'url': None,
                'message': 'No Cloudflare tunnel detected'
            }
        
        try:
            response = requests.get(f"{url}/system_stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                return {
                    'status': 'connected',
                    'url': url,
                    'comfyui_version': stats.get('system', {}).get('comfyui_version', 'unknown'),
                    'devices': stats.get('devices', []),
                    'message': f'Connected to ComfyUI via {url}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'url': url,
                'error': str(e),
                'message': f'Tunnel found but connection failed: {e}'
            }
        
        return {
            'status': 'error',
            'url': url,
            'message': 'Tunnel found but ComfyUI not responding'
        }

# Global detector instance
tunnel_detector = CloudflareTunnelDetector()

def get_dynamic_comfyui_url() -> str:
    """Get the current ComfyUI URL (either tunnel or local)"""
    # First check for registered tunnel URL from the registry
    try:
        reg_url = get_tunnel_url()
        if reg_url:
            # Test if the registered URL is still working
            try:
                response = requests.get(f"{reg_url.rstrip('/')}/system_stats", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Using registered tunnel URL: {reg_url}")
                    return reg_url
                else:
                    logger.warning(f"Registered tunnel URL not responding: {reg_url}")
            except Exception as e:
                logger.warning(f"Failed to test registered tunnel URL {reg_url}: {e}")
    except Exception as e:
        logger.debug(f"Failed to get registered tunnel URL: {e}")
    
    # Try to detect tunnel automatically
    tunnel_url = tunnel_detector.detect_tunnel_url()
    if tunnel_url:
        logger.info(f"Using auto-detected tunnel URL: {tunnel_url}")
        return tunnel_url
    
    # Fallback to local
    logger.info("Using fallback local URL: http://127.0.0.1:8188")
    return 'http://127.0.0.1:8188'

def test_tunnel_detection():
    """Test the tunnel detection system"""
    print("🔍 Testing Cloudflare Tunnel Detection")
    print("=" * 50)
    
    detector = CloudflareTunnelDetector()
    info = detector.get_tunnel_info()
    
    print(f"Status: {info['status']}")
    print(f"URL: {info.get('url', 'None')}")
    print(f"Message: {info['message']}")
    
    if info['status'] == 'connected':
        print(f"ComfyUI Version: {info.get('comfyui_version', 'unknown')}")
        print(f"Devices: {len(info.get('devices', []))} GPU(s) detected")
    
    return info['status'] == 'connected'

if __name__ == "__main__":
    test_tunnel_detection()
