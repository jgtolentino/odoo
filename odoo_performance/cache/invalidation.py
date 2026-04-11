"""
Cache invalidation helpers.

Keeping a cache consistent with the database is the hardest part of caching.
This module provides:

* :class:`CacheInvalidator` – a registry of cache objects (anything with a
  ``clear()`` method and, optionally, a ``delete(key)`` method) that can be
  cleared selectively by *tag* or wholesale.
* Helper decorators for hooking into Odoo's ``write`` / ``unlink`` / ``create``
  ORM callbacks so that the cache is automatically invalidated when records
  change.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from threading import Lock
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

_logger = logging.getLogger(__name__)


class CacheInvalidator:
    """Registry for cache objects that need coordinated invalidation.

    Caches are registered with one or more *tags* (plain strings).  When a tag
    is invalidated every cache registered under that tag is cleared.

    Usage::

        invalidator = CacheInvalidator()
        partner_cache = LRUCache(maxsize=1024)

        # Register the cache under the "res.partner" tag.
        invalidator.register(partner_cache, tags=["res.partner"])

        # Later, when partner records change:
        invalidator.invalidate("res.partner")

    :param name: Optional human-readable name for logging.
    """

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._lock = Lock()
        self._caches: Dict[str, List[Any]] = defaultdict(list)
        self._all_caches: List[Any] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, cache: Any, *, tags: Iterable[str] = ()) -> None:
        """Register *cache* for invalidation by any of the given *tags*.

        The *cache* object must implement at least a ``clear()`` method.

        :param cache: Cache object to manage.
        :param tags: Iterable of string tags that should trigger invalidation
            of this cache.
        """
        with self._lock:
            if cache not in self._all_caches:
                self._all_caches.append(cache)
            for tag in tags:
                if cache not in self._caches[tag]:
                    self._caches[tag].append(cache)

    def unregister(self, cache: Any) -> None:
        """Remove *cache* from the registry entirely.

        :param cache: Previously registered cache object.
        """
        with self._lock:
            self._all_caches = [c for c in self._all_caches if c is not cache]
            for tag in list(self._caches):
                self._caches[tag] = [c for c in self._caches[tag] if c is not cache]

    # ------------------------------------------------------------------
    # Invalidation
    # ------------------------------------------------------------------

    def invalidate(self, *tags: str) -> int:
        """Clear all caches registered under any of *tags*.

        :param tags: One or more tag strings.
        :returns: Number of caches cleared.
        """
        cleared: Set[int] = set()
        with self._lock:
            for tag in tags:
                for cache in self._caches.get(tag, []):
                    cache_id = id(cache)
                    if cache_id not in cleared:
                        cache.clear()
                        cleared.add(cache_id)
                        _logger.debug(
                            "CacheInvalidator[%s]: cleared cache %r (tag=%r)",
                            self.name,
                            getattr(cache, "__class__", type(cache)).__name__,
                            tag,
                        )
        return len(cleared)

    def invalidate_all(self) -> int:
        """Clear every registered cache.

        :returns: Number of caches cleared.
        """
        with self._lock:
            for cache in self._all_caches:
                cache.clear()
            count = len(self._all_caches)
        _logger.debug("CacheInvalidator[%s]: cleared all %d caches", self.name, count)
        return count

    def invalidate_key(self, key: Any, *tags: str) -> int:
        """Delete a single *key* from caches that support ``delete(key)``.

        Caches that do not implement ``delete`` are skipped (no full clear is
        triggered).

        :param key: Cache key to delete.
        :param tags: Tags that identify which caches to target.
        :returns: Number of caches from which the key was deleted.
        """
        deleted = 0
        with self._lock:
            for tag in tags:
                for cache in self._caches.get(tag, []):
                    if hasattr(cache, "delete"):
                        if cache.delete(key):
                            deleted += 1
        return deleted

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def tags(self) -> List[str]:
        """Return all registered tags."""
        with self._lock:
            return list(self._caches.keys())

    def __repr__(self) -> str:
        return (
            f"CacheInvalidator(name={self.name!r}, "
            f"caches={len(self._all_caches)}, "
            f"tags={len(self._caches)})"
        )


def auto_invalidate(
    invalidator: CacheInvalidator,
    tags: Iterable[str],
) -> Callable[[Any], Any]:
    """Decorator factory for Odoo ORM write/create/unlink methods.

    Wraps the decorated method so that the given *tags* are invalidated in
    *invalidator* after the original method returns successfully.

    Example – attach to ``res.partner.write``::

        @auto_invalidate(app_invalidator, tags=["res.partner"])
        def write(self, vals):
            return super().write(vals)

    :param invalidator: The :class:`CacheInvalidator` instance to use.
    :param tags: Tags to invalidate after the method runs.
    """
    tag_list = list(tags)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        import functools

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            invalidator.invalidate(*tag_list)
            return result

        return wrapper

    return decorator
