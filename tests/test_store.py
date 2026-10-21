import pytest

from tally.store import InvoiceStore


def test_add_and_list_by_customer() -> None:
    store = InvoiceStore()
    first = store.add("acme", 1000)
    store.add("globex", 500)
    store.add("acme", 250)
    assert [inv.cents for inv in store.by_customer("acme")] == [1000, 250]
    assert first.id == 1 and not first.paid


def test_add_rejects_non_positive() -> None:
    with pytest.raises(ValueError):
        InvoiceStore().add("acme", 0)


def test_mark_paid() -> None:
    store = InvoiceStore()
    inv = store.add("acme", 1000)
    assert store.mark_paid(inv.id)
    assert not store.mark_paid(999)
    assert store.by_customer("acme")[0].paid


def test_search_by_prefix() -> None:
    store = InvoiceStore()
    store.add("acme", 1000)
    store.add("globex", 500)
    store.add("acme labs", 250)
    assert [inv.customer for inv in store.search("ac")] == ["acme", "acme labs"]


def test_search_binds_the_prefix() -> None:
    store = InvoiceStore()
    store.add("acme", 1000)
    store.add("a_b", 200)
    assert store.search("x' OR '1'='1") == []
    assert [inv.customer for inv in store.search("a_")] == ["a_b"]
    assert len(store.search("")) == 2
