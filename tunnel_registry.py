import os
import json
import time
import logging

logger = logging.getLogger(__name__)

# File to persist the registered tunnel URL
REGISTRY_FILE = os.path.join("instance", "detected_tunnel.json")


def _ensure_dir():
    dirname = os.path.dirname(REGISTRY_FILE)
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname, exist_ok=True)
        except Exception:
            pass


def get_tunnel_url():
    """Return the stored tunnel URL if present, else None."""
    try:
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                url = data.get("url")
                if url:
                    return url
    except Exception as e:
        logger.debug(f"Failed to read tunnel registry: {e}")
    return None


def set_tunnel_url(url: str):
    """Store the current tunnel URL (overwrites previous)."""
    try:
        _ensure_dir()
        data = {"url": url, "ts": int(time.time())}
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        logger.info(f"Registered tunnel URL: {url}")
        return True
    except Exception as e:
        logger.error(f"Failed to write tunnel registry: {e}")
        return False


def clear_tunnel_url():
    """Remove stored tunnel URL."""
    try:
        if os.path.exists(REGISTRY_FILE):
            os.remove(REGISTRY_FILE)
            logger.info("Cleared registered tunnel URL")
            return True
    except Exception as e:
        logger.error(f"Failed to clear tunnel registry: {e}")
    return False
