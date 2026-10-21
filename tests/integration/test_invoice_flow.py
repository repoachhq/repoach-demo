from tally.money import parse_amount
from tally.service import outstanding, page
from tally.store import InvoiceStore


def test_bill_pay_and_page_through() -> None:
    store = InvoiceStore()
    for n in range(12):
        store.add("acme" if n % 3 else "globex", parse_amount(f"{n + 1}.50"))
    for inv in page(store, 1, size=5):
        store.mark_paid(inv.id)
    assert [len(page(store, n, size=5)) for n in (1, 2, 3)] == [5, 5, 2]
    assert outstanding(store, "acme") + outstanding(store, "globex") == sum(
        inv.cents for inv in store.all() if not inv.paid
    )
    assert outstanding(store, "globex") == parse_amount("7.50") + parse_amount("10.50")
