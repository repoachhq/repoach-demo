import { describe, expect, it } from "vitest";
import { formatCents, renderInvoiceTable } from "./InvoiceTable";

describe("formatCents", () => {
  it("formats cents with two places", () => {
    expect(formatCents(1234)).toBe("12.34");
    expect(formatCents(5)).toBe("0.05");
    expect(formatCents(-250)).toBe("-2.50");
  });
});

describe("renderInvoiceTable", () => {
  it("renders an empty state", () => {
    expect(renderInvoiceTable([])).toContain("No invoices");
  });

  it("escapes the customer name", () => {
    const html = renderInvoiceTable([{ id: 1, customer: "<b>acme</b>", cents: 100, paid: false }]);
    expect(html).toContain("&lt;b&gt;acme&lt;/b&gt;");
    expect(html).toContain("<td>due</td>");
  });
});
