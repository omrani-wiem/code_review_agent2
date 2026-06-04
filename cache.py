import hashlib
import json
import os
import logging


logger = logging.getLogger(__name__)


CACHE_FILE = "review_cache.json"


def _load_cache()  -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cache_key(code: str) -> str:
    return hashlib.md5(code.strip().encode()).hexdigest()


_cache: dict = _load_cache()

def get_cached(code: str):
    key = get_cache_key(code)
    if key in _cache:
        logger.info(f" Cache HIT [{key[:8]}]")
        return _cache[key]
    return None

def set_cached(code: str, result: dict):
    key = get_cache_key(code)
    _cache[key] = result
    _save_cache(_cache)
    logger.info(f" Cache SAVED [{key[:8]}]")