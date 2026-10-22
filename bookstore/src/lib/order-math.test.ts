import { test } from "node:test";
import assert from "node:assert/strict";
import { computeTotals, newOrderReference } from "./order-math.ts";

test("totals multiple lines plus delivery", () => {
  const t = computeTotals([{ unitPriceUgx: 20000, quantity: 3 }, { unitPriceUgx: 15000, quantity: 2 }], 5000);
  assert.deepEqual(t, { subtotalUgx: 90000, deliveryFeeUgx: 5000, totalUgx: 95000 });
});
test("rejects empty, bad quantity, bad price, bad fee", () => {
  assert.throws(() => computeTotals([]));
  assert.throws(() => computeTotals([{ unitPriceUgx: 100, quantity: 0 }]));
  assert.throws(() => computeTotals([{ unitPriceUgx: 100, quantity: 501 }]));
  assert.throws(() => computeTotals([{ unitPriceUgx: 1.5, quantity: 1 }]));
  assert.throws(() => computeTotals([{ unitPriceUgx: 100, quantity: 1 }], -1));
});
test("order reference format", () => {
  assert.match(newOrderReference(), /^ORD-[A-HJ-NP-Z2-9]{6}$/);
});
