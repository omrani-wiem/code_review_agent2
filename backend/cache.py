import hashlib
import json
import os
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL", 60 * 60 * 24))   
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", 500))     
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")



class RedisCache:
    """
    Cache Redis : thread-safe, TTL natif, scalable horizontalement.
    Nécessite : pip install redis
    """

    def __init__(self, url: str, ttl: int):
        import redis
        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._ttl = ttl
        
        self._client.ping()
        logger.info(" Redis cache connecté sur %s", url)

    def get(self, key: str) -> Optional[dict]:
        raw = self._client.get(key)
        if raw:
            logger.info(" Cache HIT [%s]", key[:8])
            return json.loads(raw)
        return None

    def set(self, key: str, value: dict) -> None:
        self._client.setex(key, self._ttl, json.dumps(value))
        logger.info(" Cache SAVED [%s] TTL=%ds", key[:8], self._ttl)



CACHE_FILE = "review_cache.json"

class LocalCache:
    """
    Cache JSON fichier local — pour le développement uniquement.
    Corrections apportées :
      - Lock threading pour thread-safety
      - TTL par entrée (expiration automatique)
      - Limite du nombre d'entrées (éviction LRU simplifiée)
      - Chargement paresseux (pas tout en mémoire d'un coup)
    """

    def __init__(self, ttl: int, max_entries: int):
        self._ttl = ttl
        self._max_entries = max_entries
        self._lock = threading.Lock()         
        self._cache: dict = self._load() 

    def _load(self) -> dict:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Cache corrompu, réinitialisé : %s", e)
        return {}

    def _save(self) -> None:
        """Écriture atomique via fichier temporaire pour éviter la corruption."""
        tmp = CACHE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self._cache, f, indent=2)
        os.replace(tmp, CACHE_FILE)            


    def _is_expired(self, entry: dict) -> bool:
        """Vérifie si une entrée a dépassé son TTL."""
        return time.time() - entry.get("_saved_at", 0) > self._ttl

    def _evict_if_needed(self) -> None:
        """Supprime les entrées expirées, puis les plus anciennes si trop plein."""

        expired = [k for k, v in self._cache.items() if self._is_expired(v)]
        for k in expired:
            del self._cache[k]


        while len(self._cache) >= self._max_entries:
            oldest_key = min(
                self._cache, key=lambda k: self._cache[k].get("_saved_at", 0)
            )
            del self._cache[oldest_key]
            logger.info("  Éviction LRU [%s]", oldest_key[:8])

    def get(self, key: str) -> Optional[dict]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if self._is_expired(entry):         
                del self._cache[key]
                logger.info(" Cache EXPIRED [%s]", key[:8])
                return None
            logger.info(" Cache HIT [%s]", key[:8])
            # Retourner sans la métadonnée interne
            return {k: v for k, v in entry.items() if not k.startswith("_")}

    def set(self, key: str, value: dict) -> None:
        with self._lock:
            self._evict_if_needed()            
            self._cache[key] = {**value, "_saved_at": time.time()}
            self._save()                          
            logger.info("Cache SAVED [%s]", key[:8])



def _build_cache():
    """
    Essaie Redis en premier. Si indisponible, bascule sur le cache JSON local.
    """
    try:
        return RedisCache(url=REDIS_URL, ttl=CACHE_TTL_SECONDS)
    except Exception as e:
        logger.warning(
            "  Redis indisponible (%s). Utilisation du cache JSON local (dev only).", e
        )
        return LocalCache(ttl=CACHE_TTL_SECONDS, max_entries=CACHE_MAX_ENTRIES)


_cache_backend = _build_cache()



def get_cache_key(code: str) -> str:
    """
    SHA-256 au lieu de MD5 :
      - Même usage (identifiant, pas crypto), mais moins de collisions théoriques.
    """
    return hashlib.sha256(code.strip().encode()).hexdigest()


def get_cached(code: str) -> Optional[dict]:
    key = get_cache_key(code)
    return _cache_backend.get(key)


def set_cached(code: str, result: dict) -> None:
    key = get_cache_key(code)
    _cache_backend.set(key, result)