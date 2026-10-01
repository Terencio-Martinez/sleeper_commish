import json
from pathlib import Path

import httpx

CACHE_PATH = Path("/app/data/players.json")
_cache: dict | None = None


def _index() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if CACHE_PATH.exists():
        _cache = json.loads(CACHE_PATH.read_text())
        return _cache
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    r = httpx.get("https://api.sleeper.app/v1/players/nfl", timeout=120.0)
    r.raise_for_status()
    _cache = r.json()
    CACHE_PATH.write_text(json.dumps(_cache))
    return _cache


def player_name(player_id: str) -> str:
    p = _index().get(str(player_id))
    if not p:
        return f"player:{player_id}"
    return p.get("full_name") or f"player:{player_id}"