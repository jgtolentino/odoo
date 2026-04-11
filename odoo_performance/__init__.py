"""
Odoo Performance Optimization Utilities
========================================

A collection of utilities to improve Odoo application performance across:
- ORM query optimization (batch reads, prefetch management)
- Caching (LRU, memoization, invalidation)
- Database connection pool tuning
- Memory management helpers
"""

from .orm.batch import BatchProcessor, prefetch_fields
from .orm.query_optimizer import QueryOptimizer
from .cache.lru import lru_cache_method, memoize
from .cache.invalidation import CacheInvalidator
from .db.pool import ConnectionPoolManager
from .db.query_analyzer import QueryAnalyzer

__all__ = [
    "BatchProcessor",
    "prefetch_fields",
    "QueryOptimizer",
    "lru_cache_method",
    "memoize",
    "CacheInvalidator",
    "ConnectionPoolManager",
    "QueryAnalyzer",
]

__version__ = "1.0.0"
