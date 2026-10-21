# SP-TALLY-INVOICES — Search, page count and due total

Add `InvoiceStore.search`, `service.page_count` and `dueTotal`, each pinned by a test that names the contract it protects.

## Step 1 — Search by customer prefix with bound parameters

- **Files**: `src/tally/store.py`, `tests/test_store.py`
- **Action**: Add `InvoiceStore.search(prefix)`; the prefix is a bound parameter and matches literally.
- **Commit**: `feat(store): search invoices by customer prefix`
- **Done when**: `pytest -q tests/test_store.py` passes.
- **Unit tests**: `tests/test_store.py::test_search_binds_the_prefix`

## Step 2 — Page count rounds up

- **Files**: `src/tally/service.py`, `tests/test_service.py`, `tests/integration/test_invoice_flow.py`
- **Action**: Add `page_count(store, size=10)`, the number of non-empty pages `page` serves.
- **Commit**: `feat(service): count the pages`
- **Done when**: `pytest -q tests/test_service.py` passes.
- **Unit tests**: `tests/test_service.py::test_page_count_rounds_up`

## Step 3 — Due total in the invoice table module

- **Files**: `frontend/src/InvoiceTable.ts`, `frontend/src/InvoiceTable.test.ts`
- **Action**: Add `dueTotal(invoices)`, the formatted sum of the unpaid invoices.
- **Commit**: `feat(frontend): total what is due`
- **Done when**: `cd frontend && npx vitest run` passes.
- **Unit tests**: `frontend/src/InvoiceTable.test.ts::dueTotal::sums the unpaid invoices only`


## Integration tests

- `tests/integration/test_invoice_flow.py`

<!-- repoach-action-plan -->
```json
{
  "spec_id": "SP-TALLY-INVOICES",
  "title": "Search, page count and due total",
  "summary": "Add InvoiceStore.search, service.page_count and dueTotal, each pinned by a test that names the contract it protects.",
  "steps": [
    {
      "index": 1,
      "title": "Search by customer prefix with bound parameters",
      "files": ["src/tally/store.py", "tests/test_store.py"],
      "action": "Add InvoiceStore.search(prefix); the prefix is a bound parameter and matches literally.",
      "commit_message": "feat(store): search invoices by customer prefix",
      "done_when": "`pytest -q tests/test_store.py` passes.",
      "unit_tests": ["tests/test_store.py::test_search_binds_the_prefix"]
    },
    {
      "index": 2,
      "title": "Page count rounds up",
      "files": ["src/tally/service.py", "tests/test_service.py", "tests/integration/test_invoice_flow.py"],
      "action": "Add page_count(store, size=10), the number of non-empty pages page serves.",
      "commit_message": "feat(service): count the pages",
      "done_when": "`pytest -q tests/test_service.py` passes.",
      "unit_tests": ["tests/test_service.py::test_page_count_rounds_up"]
    },
    {
      "index": 3,
      "title": "Due total in the invoice table module",
      "files": ["frontend/src/InvoiceTable.ts", "frontend/src/InvoiceTable.test.ts"],
      "action": "Add dueTotal(invoices), the formatted sum of the unpaid invoices.",
      "commit_message": "feat(frontend): total what is due",
      "done_when": "`cd frontend && npx vitest run` passes.",
      "unit_tests": ["frontend/src/InvoiceTable.test.ts::dueTotal::sums the unpaid invoices only"]
    }
  ],
  "integration_tests": ["tests/integration/test_invoice_flow.py"]
}
```
