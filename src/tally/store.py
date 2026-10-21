"""SQLite-backed invoice store."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Invoice:
    """One invoice row."""

    id: int
    customer: str
    cents: int
    paid: bool


class InvoiceStore:
    """Persist invoices in a SQLite database (``:memory:`` by default)."""

    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS invoices ("
            "id INTEGER PRIMARY KEY, customer TEXT NOT NULL, "
            "cents INTEGER NOT NULL, paid INTEGER NOT NULL DEFAULT 0)"
        )

    def add(self, customer: str, cents: int) -> Invoice:
        """Insert an unpaid invoice and return it."""
        if cents <= 0:
            raise ValueError("an invoice must be positive")
        cur = self._db.execute(
            "INSERT INTO invoices (customer, cents) VALUES (?, ?)", (customer, cents)
        )
        self._db.commit()
        return Invoice(int(cur.lastrowid or 0), customer, cents, False)

    def mark_paid(self, invoice_id: int) -> bool:
        """Mark one invoice paid; return whether it existed."""
        cur = self._db.execute("UPDATE invoices SET paid = 1 WHERE id = ?", (invoice_id,))
        self._db.commit()
        return cur.rowcount == 1

    def by_customer(self, customer: str) -> list[Invoice]:
        """Return the invoices of one customer, oldest first."""
        rows = self._db.execute(
            "SELECT id, customer, cents, paid FROM invoices WHERE customer = ? ORDER BY id",
            (customer,),
        ).fetchall()
        return [Invoice(r[0], r[1], r[2], bool(r[3])) for r in rows]

    def all(self) -> list[Invoice]:
        """Return every invoice, oldest first."""
        rows = self._db.execute("SELECT id, customer, cents, paid FROM invoices ORDER BY id")
        return [Invoice(r[0], r[1], r[2], bool(r[3])) for r in rows.fetchall()]

    def search(self, prefix: str) -> list[Invoice]:
        """Return the invoices whose customer starts with ``prefix``, oldest first."""
        rows = self._db.execute(
            "SELECT id, customer, cents, paid FROM invoices "
            "WHERE substr(customer, 1, length(?)) = ? ORDER BY id",
            (prefix, prefix),
        )
        return [Invoice(r[0], r[1], r[2], bool(r[3])) for r in rows.fetchall()]
