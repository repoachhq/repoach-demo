"""Use cases over the store: outstanding balance and paging."""

from __future__ import annotations

from tally.store import Invoice, InvoiceStore


def outstanding(store: InvoiceStore, customer: str) -> int:
    """Return the unpaid total of one customer, in cents."""
    return sum(inv.cents for inv in store.by_customer(customer) if not inv.paid)


def page(store: InvoiceStore, number: int, size: int = 10) -> list[Invoice]:
    """Return page ``number`` (1-based) of all invoices, ``size`` per page."""
    if number < 1 or size < 1:
        raise ValueError("page number and size start at 1")
    start = (number - 1) * size
    return store.all()[start : start + size]


def page_count(store: InvoiceStore, size: int = 10) -> int:
    """Return how many pages of ``size`` invoices ``page`` serves."""
    if size < 1:
        raise ValueError("page size starts at 1")
    return len(store.all()) // size
