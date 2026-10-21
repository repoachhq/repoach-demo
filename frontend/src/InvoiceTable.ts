export interface Invoice {
  id: number;
  customer: string;
  cents: number;
  paid: boolean;
}

export function formatCents(cents: number): string {
  const sign = cents < 0 ? "-" : "";
  const abs = Math.abs(cents);
  return `${sign}${Math.floor(abs / 100)}.${String(abs % 100).padStart(2, "0")}`;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function renderInvoiceTable(invoices: Invoice[]): string {
  if (invoices.length === 0) {
    return '<p class="empty">No invoices</p>';
  }
  const rows = invoices
    .map(
      (inv) =>
        `<tr><td>${inv.id}</td><td>${escapeHtml(inv.customer)}</td>` +
        `<td>${formatCents(inv.cents)}</td><td>${inv.paid ? "paid" : "due"}</td></tr>`,
    )
    .join("");
  return `<table><tbody>${rows}</tbody></table>`;
}

export function dueTotal(invoices: Invoice[]): string {
  return formatCents(invoices.filter((inv) => !inv.paid).reduce((sum, inv) => sum + inv.cents, 0));
}
