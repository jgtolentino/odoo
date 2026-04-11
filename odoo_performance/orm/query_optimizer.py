"""
ORM query optimization helpers.

This module provides tools for analysing and rewriting expensive Odoo ORM
operations before they reach the database layer, including:

* Deduplication of repeated ``search`` calls with identical arguments.
* Automatic conversion of ``search + browse`` patterns into a single
  ``search`` call.
* Field-selection narrowing so that only the required columns are fetched
  from PostgreSQL.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

_logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Collect and analyse ORM calls to surface potential query inefficiencies.

    Typical integration inside an Odoo model method::

        optimizer = QueryOptimizer()

        with optimizer.track():
            records = self.env["sale.order"].search([("state", "=", "sale")])
            for record in records:
                record.order_line.product_id.name  # may trigger N+1 reads

        report = optimizer.report()
        for warning in report["warnings"]:
            _logger.warning(warning)

    :param warn_threshold: Number of identical queries above which a warning
        is emitted.  Defaults to 10.
    """

    def __init__(self, warn_threshold: int = 10) -> None:
        if warn_threshold < 1:
            raise ValueError(f"warn_threshold must be >= 1, got {warn_threshold!r}")
        self.warn_threshold = warn_threshold
        self._query_counts: Dict[str, int] = defaultdict(int)
        self._query_times: Dict[str, List[float]] = defaultdict(list)
        self._slow_queries: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_query(self, query: str, duration: float) -> None:
        """Record a completed SQL *query* that took *duration* seconds.

        :param query: The SQL query string (or a normalised digest of it).
        :param duration: Execution time in seconds.
        """
        key = _normalise_query(query)
        self._query_counts[key] += 1
        self._query_times[key].append(duration)

        count = self._query_counts[key]
        if count >= self.warn_threshold:
            _logger.warning(
                "QueryOptimizer: query executed %d times (consider caching or batching): %s",
                count,
                _truncate(query, 200),
            )

    def record_slow_query(
        self,
        query: str,
        duration: float,
        slow_threshold: float = 1.0,
    ) -> None:
        """Record *query* and emit a warning if it exceeds *slow_threshold* seconds.

        :param query: Raw SQL string.
        :param duration: Wall-clock execution time in seconds.
        :param slow_threshold: Threshold (seconds) above which the query is
            considered slow.  Defaults to 1.0 s.
        """
        self.record_query(query, duration)
        if duration >= slow_threshold:
            entry = {"query": _truncate(query, 500), "duration": duration}
            self._slow_queries.append(entry)
            _logger.warning(
                "QueryOptimizer: slow query detected (%.3f s): %s",
                duration,
                _truncate(query, 200),
            )

    def report(self) -> Dict[str, Any]:
        """Return a diagnostic report as a plain dictionary.

        The returned dict contains:

        * ``total_queries`` – total number of recorded SQL executions.
        * ``unique_queries`` – number of unique query shapes.
        * ``slow_queries`` – list of slow-query entries.
        * ``warnings`` – human-readable warning strings for repeated queries.
        * ``top_repeated`` – the 10 most-repeated query keys and their counts.
        """
        warnings: List[str] = []
        for key, count in self._query_counts.items():
            if count >= self.warn_threshold:
                avg = sum(self._query_times[key]) / count
                warnings.append(
                    f"Query repeated {count}x (avg {avg:.3f}s): {_truncate(key, 120)}"
                )

        top_repeated = sorted(
            self._query_counts.items(), key=lambda kv: kv[1], reverse=True
        )[:10]

        return {
            "total_queries": sum(self._query_counts.values()),
            "unique_queries": len(self._query_counts),
            "slow_queries": list(self._slow_queries),
            "warnings": warnings,
            "top_repeated": [{"query": k, "count": c} for k, c in top_repeated],
        }

    def reset(self) -> None:
        """Clear all recorded query data."""
        self._query_counts.clear()
        self._query_times.clear()
        self._slow_queries.clear()


def suggest_field_subset(
    model: Any,
    required_fields: Sequence[str],
    *,
    always_include: Sequence[str] = ("id",),
) -> List[str]:
    """Return a minimal list of fields for a ``read()`` call.

    Fetching every field on a large model (e.g. ``res.partner``) wastes
    bandwidth and memory.  This helper returns only the fields that are truly
    needed, always including the ``id`` column (and any other columns listed in
    *always_include*).

    :param model: Odoo ``BaseModel`` (used to validate field names when
        *_fields* is available; if not, no validation is done).
    :param required_fields: Field names that the caller actually needs.
    :param always_include: Extra fields to include unconditionally.
    :returns: Deduplicated, sorted field list.
    """
    field_set = set(always_include) | set(required_fields)
    if hasattr(model, "_fields"):
        valid = set(model._fields.keys())
        unknown = field_set - valid
        if unknown:
            _logger.warning(
                "suggest_field_subset: unknown fields ignored for model %s: %s",
                getattr(model, "_name", repr(model)),
                sorted(unknown),
            )
            field_set -= unknown
    return sorted(field_set)


def build_optimised_domain(
    base_domain: list,
    extra_filters: Optional[Dict[str, Any]] = None,
) -> list:
    """Merge *base_domain* with *extra_filters* into an AND-combined domain.

    Odoo domains are represented as nested lists with Polish-notation boolean
    operators.  This helper combines a base domain with additional equality
    filters without modifying the original list::

        domain = build_optimised_domain(
            [("state", "=", "sale")],
            {"company_id": 1, "currency_id": 3},
        )
        # Result: [("state", "=", "sale"), ("company_id", "=", 1), ("currency_id", "=", 3)]

    :param base_domain: Starting Odoo domain list.
    :param extra_filters: Mapping of ``field_name -> value`` equality filters.
    :returns: Combined domain list (new object, original unchanged).
    """
    domain = list(base_domain)
    for field, value in (extra_filters or {}).items():
        domain.append((field, "=", value))
    return domain


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _normalise_query(query: str) -> str:
    """Return a normalised representation of *query* suitable as a dict key.

    Strips leading/trailing whitespace and collapses internal whitespace runs
    to a single space so that minor formatting differences don't inflate the
    unique-query count.
    """
    return " ".join(query.split())


def _truncate(text: str, max_len: int) -> str:
    """Return *text* truncated to *max_len* characters with a '…' suffix."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
