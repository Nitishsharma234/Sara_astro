"""Minimal, opt-in on-disk cache for catalog lookups.

Phase 1 deliberately keeps this simple: one JSON file per cache namespace
in a platform-appropriate user cache directory, no expiry policy beyond
"clear it yourself". This is enough to avoid re-querying SIMBAD every time
during interactive development; a more sophisticated (TTL-based, size-
bounded) cache can replace this later without changing the public API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platformdirs import user_cache_dir

_APP_NAME = "sara_astro"


def _cache_dir() -> Path:
    path = Path(user_cache_dir(_APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_file(namespace: str) -> Path:
    safe_namespace = "".join(c if c.isalnum() else "_" for c in namespace)
    return _cache_dir() / f"{safe_namespace}.json"


def get(namespace: str, key: str) -> Any | None:
    """Return the cached value for ``key`` in ``namespace``, or ``None``."""
    file = _cache_file(namespace)
    if not file.exists():
        return None
    try:
        data = json.loads(file.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data.get(key)


def set(namespace: str, key: str, value: Any) -> None:
    """Store ``value`` under ``key`` in ``namespace``."""
    file = _cache_file(namespace)
    data: dict[str, Any] = {}
    if file.exists():
        try:
            data = json.loads(file.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
    data[key] = value
    file.write_text(json.dumps(data))


def clear(namespace: str | None = None) -> None:
    """Clear the cache for one namespace, or every namespace if ``None``."""
    if namespace is not None:
        file = _cache_file(namespace)
        if file.exists():
            file.unlink()
        return
    for file in _cache_dir().glob("*.json"):
        file.unlink()
