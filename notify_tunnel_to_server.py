#!/usr/bin/env python3
"""
notify_tunnel_to_server.py

Tail a cloudflared log (or any file/STDOUT capture) and POST the detected trycloudflare URL
to your deployed Railway app's /register-tunnel webhook.

Usage:
  python notify_tunnel_to_server.py --log "C:\path\to\cloudflared.log" \
    --webhook "https://my-railway-app.up.railway.app/register-tunnel" \
    --secret "my_shared_secret"

If you omit --webhook or --secret the script will try to read these from environment:
  RAILWAY_WEBHOOK
  REGISTER_TUNNEL_SECRET

Behavior:
 - Watches the log file for the first occurrence of a trycloudflare URL (https://xxxxx.trycloudflare.com)
 - Validates the URL (basic check) and tries to POST JSON {"url": "..."} with header X-TUNNEL-SECRET
 - Retries posting a few times on failure, then exits successfully if server accepts the URL
 - Optionally prints verbose diagnostics
"""

import argparse
import re
import time
import requests
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("notify_tunnel")

URL_PATTERN = re.compile(r"(https://[a-z0-9-]+\.trycloudflare\.com)", re.IGNORECASE)


def tail_file(path):
    """Yield new lines appended to file (like tail -f). Blocks until file appears."""
    while True:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                # Go to end
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    yield line
        except FileNotFoundError:
            logger.info("Log file not found, waiting for it to appear: %s", path)
            time.sleep(1)
        except Exception as e:
            logger.error("Error tailing file: %s", e)
            time.sleep(1)


def find_url_in_line(line):
    m = URL_PATTERN.search(line)
    if m:
        return m.group(1).rstrip("/")
    return None


def post_url(webhook, secret, url, timeout=8, max_attempts=5):
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


def main():
    parser = argparse.ArgumentParser(description="Notify Railway app of trycloudflare tunnel URL")
    parser.add_argument("--log", "-l", help="Path to cloudflared log file to watch", required=True)
    parser.add_argument("--webhook", "-w", help="Webhook URL (e.g. https://app/.../register-tunnel)")
    parser.add_argument("--secret", "-s", help="Shared secret for X-TUNNEL-SECRET header")
    parser.add_argument("--once", action="store_true", help="Exit after successfully posting once")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.WARNING)

    webhook = args.webhook or os.environ.get("RAILWAY_WEBHOOK") or os.environ.get("REGISTER_TUNNEL_WEBHOOK")
    secret = args.secret or os.environ.get("REGISTER_TUNNEL_SECRET")

    if not webhook:
        logger.error("No webhook provided. Set --webhook or RAILWAY_WEBHOOK environment variable.")
        sys.exit(2)
    if not secret:
        logger.error("No secret provided. Set --secret or REGISTER_TUNNEL_SECRET environment variable.")
        sys.exit(2)

    logger.info("Watching log: %s", args.log)
    logger.info("Webhook: %s", webhook)
    # Do not print secret in logs

    for line in tail_file(args.log):
        url = find_url_in_line(line)
        if url:
            logger.info("Detected trycloudflare URL: %s", url)
            ok, resp = post_url(webhook, secret, url)
            if ok:
                logger.info("Successfully registered tunnel URL with server.")
                if args.once:
                    logger.info("Exiting due to --once flag.")
                    return 0
                # Keep running: if tunnel rotates, we may detect another one later.
                # To avoid duplicate posts flooding the server, sleep a bit before watching again.
                time.sleep(2)
            else:
                logger.error("Failed to register tunnel URL with server. Stopping.")
                # If resp exists and is client error, show details
                if resp is not None:
                    logger.error("Server response: %d %s", resp.status_code, resp.text[:400])
                # Continue watching — cloudflared sometimes prints multiple lines; maybe next will work
                time.sleep(5)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
