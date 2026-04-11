"""
LRU caching decorators for Odoo model methods.

Odoo already ships a ``tools.cache`` decorator that caches by positional and
keyword arguments.  The helpers in this module extend that pattern with:

* A method-level LRU cache that automatically respects the ``maxsize``
  parameter and is safe to use on instance methods (binds to ``type(self)``
  rather than ``self`` so the cache is shared across instances of the same
  model class).
* A simpler ``memoize`` decorator for pure functions.
* Per-key TTL (time-to-live) expiry support.
"""

from __future__ import annotations

import functools
import logging
import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

_logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Sentinel used to distinguish "key not found" from ``None`` values.
_MISSING = object()


class _TTLEntry:
    """Cache entry that carries an optional expiry timestamp."""

    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl: Optional[float]) -> None:
        self.value = value
        self.expires_at: Optional[float] = (time.monotonic() + ttl) if ttl is not None else None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.monotonic() >= self.expires_at


class LRUCache:
    """Thread-safe LRU cache with optional per-entry TTL.

    :param maxsize: Maximum number of entries.  When the cache is full the
        least-recently-used entry is evicted first.
    :param ttl: Optional time-to-live in seconds.  Expired entries are treated
        as cache misses and evicted lazily on the next access.
    """

    def __init__(self, maxsize: int = 128, ttl: Optional[float] = None) -> None:
        if maxsize < 1:
            raise ValueError(f"maxsize must be >= 1, got {maxsize!r}")
        if ttl is not None and ttl <= 0:
            raise ValueError(f"ttl must be > 0, got {ttl!r}")
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: OrderedDict[Any, _TTLEntry] = OrderedDict()
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: Any, default: Any = _MISSING) -> Any:
        """Return the cached value for *key*, or *default* on a miss.

        :raises KeyError: If *key* is missing and no *default* is provided.
        """
        with self._lock:
            entry = self._store.get(key, None)
            if entry is None or entry.is_expired():
                if entry is not None:
                    del self._store[key]
                self.misses += 1
                if default is _MISSING:
                    raise KeyError(key)
                return default
            self._store.move_to_end(key)
            self.hits += 1
            return entry.value

    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """Store *value* under *key*.

        :param ttl: Per-entry TTL override.  Falls back to the instance-level
            ``ttl`` if not provided.
        """
        effective_ttl = ttl if ttl is not None else self.ttl
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = _TTLEntry(value, effective_ttl)
            if len(self._store) > self.maxsize:
                evicted_key, _ = self._store.popitem(last=False)
                _logger.debug("LRUCache: evicted key %r", evicted_key)

    def delete(self, key: Any) -> bool:
        """Remove *key* from the cache.

        :returns: ``True`` if the key existed, ``False`` otherwise.
        """
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()
            self.hits = 0
            self.misses = 0

    def __contains__(self, key: Any) -> bool:
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)

    @property
    def info(self) -> Dict[str, Any]:
        """Return cache statistics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total else 0.0
            return {
                "maxsize": self.maxsize,
                "currsize": len(self._store),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "ttl": self.ttl,
            }


def lru_cache_method(
    maxsize: int = 128,
    ttl: Optional[float] = None,
    key_fields: Optional[Tuple[str, ...]] = None,
) -> Callable[[F], F]:
    """Decorator that adds an LRU cache to an Odoo model *instance method*.

    The cache key is built from the *type* of ``self`` (so the same cache is
    shared across all instances of the same model class) plus the remaining
    positional and keyword arguments.

    Optionally, *key_fields* may list Odoo field names that are read from
    ``self`` and included in the cache key (e.g. ``("company_id",)``).

    Example::

        class ResPartner(models.Model):
            _name = "res.partner"

            @lru_cache_method(maxsize=256, ttl=300)
            def get_display_address(self):
                return self.env["ir.qweb"]._render(...)

    :param maxsize: Maximum number of entries per decorated method.
    :param ttl: Optional time-to-live in seconds.
    :param key_fields: Odoo field names on ``self`` to include in the key.
    """
    _cache: LRUCache = LRUCache(maxsize=maxsize, ttl=ttl)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            extra: Tuple[Any, ...] = ()
            if key_fields:
                extra = tuple(getattr(self, f, None) for f in key_fields)
            key = (type(self), getattr(self, "id", None), extra, args, tuple(sorted(kwargs.items())))
            try:
                return _cache.get(key)
            except KeyError:
                result = func(self, *args, **kwargs)
                _cache.set(key, result)
                return result

        wrapper._lru_cache = _cache  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def memoize(
    maxsize: int = 128,
    ttl: Optional[float] = None,
) -> Callable[[F], F]:
    """Memoisation decorator for *pure functions* (no ``self`` argument).

    Unlike :func:`functools.lru_cache`, this variant supports an optional TTL
    and exposes hit/miss statistics via the ``_lru_cache`` attribute::

        @memoize(maxsize=512, ttl=60)
        def compute_tax_rate(country_code: str, product_type: str) -> float:
            ...

        rate = compute_tax_rate("US", "physical")
        print(compute_tax_rate._lru_cache.info)

    :param maxsize: Maximum cache size.
    :param ttl: Optional TTL in seconds.
    """
    _cache: LRUCache = LRUCache(maxsize=maxsize, ttl=ttl)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            try:
                return _cache.get(key)
            except KeyError:
                result = func(*args, **kwargs)
                _cache.set(key, result)
                return result

        wrapper._lru_cache = _cache  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
