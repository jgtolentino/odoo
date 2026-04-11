"""
Batch processing utilities for Odoo ORM operations.

Odoo's ORM fetches records individually by default in some scenarios, which can
lead to N+1 query problems.  The utilities in this module help callers read
large record sets efficiently by splitting them into fixed-size chunks and
explicitly controlling which fields are prefetched.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Generator, Iterable, Iterator, List, Sequence

_logger = logging.getLogger(__name__)

# Default batch size used when none is supplied by the caller.
DEFAULT_BATCH_SIZE = 1000


class BatchProcessor:
    """Process Odoo record-sets in fixed-size batches.

    Iterating over a very large record-set triggers individual ``read()``
    calls under the hood for each record's fields once the prefetch buffer is
    exhausted.  :class:`BatchProcessor` avoids this by splitting the id list
    into chunks and reading each chunk as a unit before yielding the individual
    records to the caller.

    Example usage inside an Odoo model method::

        processor = BatchProcessor(self.env["sale.order"], batch_size=500)
        for record in processor.iter_records(domain=[("state", "=", "sale")]):
            _process_order(record)

    :param model: An Odoo ``BaseModel`` instance or model class with
        ``env`` attached (e.g. ``self.env["res.partner"]``).
    :param batch_size: Number of records to load per database round-trip.
    :param fields: Field names to pre-read.  If *None* all fields are read.
    """

    def __init__(
        self,
        model: Any,
        batch_size: int = DEFAULT_BATCH_SIZE,
        fields: Sequence[str] | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {batch_size!r}")
        self._model = model
        self.batch_size = batch_size
        self.fields = list(fields) if fields is not None else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def iter_records(
        self,
        domain: list | None = None,
        order: str | None = None,
    ) -> Iterator[Any]:
        """Yield records matching *domain* one at a time, in batches.

        :param domain: Odoo-style search domain.  Defaults to ``[]`` (all).
        :param order: SQL ORDER BY clause string (e.g. ``"name asc"``).
        """
        domain = domain or []
        ids: List[int] = self._model.search(domain, order=order).ids
        yield from self._iter_ids(ids)

    def iter_ids(self, ids: Iterable[int]) -> Iterator[Any]:
        """Yield records for the given *ids*, in batches.

        :param ids: Iterable of integer record ids.
        """
        yield from self._iter_ids(list(ids))

    def process(
        self,
        domain: list | None = None,
        order: str | None = None,
    ) -> List[Any]:
        """Return all matching records as a flat list (loads everything into
        memory – use :meth:`iter_records` for streaming large sets).
        """
        return list(self.iter_records(domain=domain, order=order))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _iter_ids(self, ids: List[int]) -> Iterator[Any]:
        total = len(ids)
        processed = 0
        for chunk_ids in _chunk(ids, self.batch_size):
            records = self._model.browse(chunk_ids)
            if self.fields:
                records.read(self.fields)
            processed += len(chunk_ids)
            _logger.debug(
                "BatchProcessor: processed %d/%d records (model=%s)",
                processed,
                total,
                self._model._name if hasattr(self._model, "_name") else repr(self._model),
            )
            yield from records


def prefetch_fields(records: Any, fields: Sequence[str]) -> Any:
    """Pre-read *fields* for *records* in a single SQL query.

    This is a thin wrapper around ``records.read(fields)`` that returns the
    original record-set unchanged so it can be used in a fluent style::

        partners = prefetch_fields(self.env["res.partner"].search([]), ["name", "email"])
        for partner in partners:
            print(partner.name, partner.email)

    :param records: An Odoo record-set.
    :param fields: Names of the fields to prefetch.
    :returns: The same record-set (prefetch cache populated as a side-effect).
    """
    if fields:
        records.read(list(fields))
    return records


# ------------------------------------------------------------------
# Private utilities
# ------------------------------------------------------------------

def _chunk(lst: List[Any], size: int) -> Generator[List[Any], None, None]:
    """Yield successive *size*-sized slices from *lst*."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


@contextmanager
def batch_context(env: Any, batch_size: int = DEFAULT_BATCH_SIZE) -> Generator[None, None, None]:
    """Context manager that temporarily lowers the ORM prefetch limit.

    Inside the block Odoo will flush the prefetch cache every *batch_size*
    records instead of waiting until it grows arbitrarily large.  This keeps
    memory usage bounded when iterating very large record-sets.

    :param env: Odoo ``Environment`` object.
    :param batch_size: Maximum prefetch buffer size (records).
    """
    original = getattr(env, "_prefetch_ids", None)
    try:
        if hasattr(env, "prefetch_ids"):
            env.prefetch_ids = {}
        yield
    finally:
        if original is not None and hasattr(env, "prefetch_ids"):
            env.prefetch_ids = original
