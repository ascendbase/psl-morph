#!/usr/bin/env python3
"""
Simple tunnel notifier that uses the existing tunnel detection system
"""

import argparse
import time
import requests
import logging
import os
import sys
import subprocess
import psutil

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloudflare_tunnel_detector import get_dynamic_comfyui_url, tunnel_detector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("notify_tunnel_simple")

def post_url(webhook, secret, url, timeout=8, max_attempts=5):
    """Post tunnel URL to webhook"""
    headers = {"X-TUNNEL-SECRET": secret}
    payload = {"url": url}
    attempt = 0
    backoff = 1.0

    while attempt < max_attempts:
        attempt += 1
        try:
            logger.info("Posting detected URL to webhook (attempt %d): %s", attempt, webhook)
            resp = requests.post(webhook, json=payload, headers=headers, timeout=timeout)
            logger.info("Webhook response: %d %s", resp.status_code, resp.text.strip()[:120])
            if resp.status_code == 200:
                return True, resp
            elif resp.status_code in (400, 401, 403):
                # Client error — don't retry endlessly
                return False, resp
            else:
                # Server error — retry
                logger.warning("Server returned %d, retrying after %.1fs", resp.status_code, backoff)
        except requests.exceptions.RequestException as e:
            logger.warning("Request failed (attempt %d): %s", attempt, e)

        time.sleep(backoff)
        backoff = min(backoff * 2, 30)

    return False, None

def wait_for_cloudflared():
    """Wait for cloudflared process to start"""
    logger.info("Waiting for cloudflared process to start...")
    max_wait = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                    logger.info(f"Found cloudflared process: PID {proc.info['pid']}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(1)
    
    logger.warning("cloudflared process not found, continuing anyway...")
    return False

def main():
    parser = argparse.ArgumentParser(description="Notify Railway app of tunnel URL using detection system")
    parser.add_argument("--webhook", "-w", help="Webhook URL", required=True)
    parser.add_argument("--secret", "-s", help="Shared secret for X-TUNNEL-SECRET header", required=True)
    parser.add_argument("--once", action="store_true", help="Exit after successfully posting once")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting tunnel URL detection and notification...")
    logger.info("Webhook: %s", args.webhook)
    
    # Wait for cloudflared to start
    wait_for_cloudflared()
    
    # Give cloudflared time to establish tunnel
    logger.info("Waiting 10 seconds for tunnel to establish...")
    time.sleep(10)
    
    max_attempts = 30  # Try for up to 5 minutes
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        logger.info(f"Detection attempt {attempt}/{max_attempts}")
        
        # Try to get tunnel URL using our detection system
        try:
            url = get_dynamic_comfyui_url()
            if url and url != "http://localhost:8188":
                logger.info("Detected tunnel URL: %s", url)
                
                # Post to webhook
                ok, resp = post_url(args.webhook, args.secret, url)
                if ok:
                    logger.info("Successfully registered tunnel URL with server.")
                    if args.once:
                        logger.info("Exiting due to --once flag.")
                        return 0
                    else:
                        # Keep monitoring for URL changes
                        time.sleep(30)
                        continue
                else:
                    logger.error("Failed to register tunnel URL with server.")
                    if resp is not None:
                        logger.error("Server response: %d %s", resp.status_code, resp.text[:400])
            else:
                logger.info("No tunnel URL detected yet, waiting...")
        
        except Exception as e:
            logger.error(f"Error during detection: {e}")
        
        time.sleep(10)  # Wait 10 seconds between attempts
    
    logger.error("Failed to detect tunnel URL after maximum attempts")
    return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
