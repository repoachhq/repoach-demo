import { describe, expect, it } from "vitest";
import { dueTotal, formatCents, renderInvoiceTable } from "./InvoiceTable";

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

describe("dueTotal", () => {
  it("sums the unpaid invoices only", () => {
    expect(
      dueTotal([
        { id: 1, customer: "acme", cents: 1000, paid: false },
        { id: 2, customer: "acme", cents: 250, paid: true },
        { id: 3, customer: "globex", cents: 5, paid: false },
      ]),
    ).toBe("10.05");
    expect(dueTotal([])).toBe("0.00");
  });
});
