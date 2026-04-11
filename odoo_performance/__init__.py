"""
Odoo Performance Optimization Utilities
========================================

A collection of utilities to improve Odoo application performance across:
- ORM query optimization (batch reads, prefetch management)
- Caching (LRU, memoization, invalidation)
"""

from .orm.batch import BatchProcessor, prefetch_fields
from .orm.query_optimizer import QueryOptimizer
from .cache.lru import lru_cache_method, memoize
from .cache.invalidation import CacheInvalidator

__all__ = [
    "BatchProcessor",
    "prefetch_fields",
    "QueryOptimizer",
    "lru_cache_method",
    "memoize",
    "CacheInvalidator",
]

__version__ = "1.0.0"
