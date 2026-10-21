import pytest

from tally.service import outstanding, page, page_count
from tally.store import InvoiceStore


def _store(n: int) -> InvoiceStore:
    store = InvoiceStore()
    for i in range(n):
        store.add("acme" if i % 2 == 0 else "globex", 100 * (i + 1))
    return store


def test_outstanding_ignores_paid() -> None:
    store = _store(4)
    store.mark_paid(1)
    assert outstanding(store, "acme") == 300
    assert outstanding(store, "globex") == 600


def test_page_sizes() -> None:
    store = _store(25)
    assert [len(page(store, n)) for n in (1, 2, 3, 4)] == [10, 10, 5, 0]
    assert page(store, 2)[0].id == 11


def test_page_rejects_zero() -> None:
    with pytest.raises(ValueError):
        page(_store(1), 0)


def test_page_count() -> None:
    assert page_count(_store(20)) == 2
    assert page_count(_store(20), size=5) == 4
