import sys
import time
import re
import logging
from tunnel_registry import set_tunnel_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("register_tunnel")

if len(sys.argv) < 2:
    print("Usage: register_tunnel_from_log.py <cloudflared_log_path>")
    sys.exit(1)

log_path = sys.argv[1]
pattern = re.compile(r'(https://[a-z0-9-]+\.trycloudflare\.com)')

def tail_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            # Seek to end
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                yield line
    except Exception as e:
        logger.error(f"Failed to tail log {path}: {e}")
        raise

def main():
    logger.info(f"Watching cloudflared logfile: {log_path}")
    for line in tail_file(log_path):
        m = pattern.search(line)
        if m:
            url = m.group(1)
            logger.info(f"Detected tunnel URL: {url}")
            try:
                ok = set_tunnel_url(url)
                if ok:
                    logger.info("Tunnel URL registered successfully")
                else:
                    logger.error("Failed to register tunnel URL")
            except Exception as e:
                logger.error(f"Error registering tunnel URL: {e}")

if __name__ == "__main__":
    main()
