export interface PricedLine { unitPriceUgx: number; quantity: number }
export const MAX_QTY_PER_LINE = 500;

export function computeTotals(lines: PricedLine[], deliveryFeeUgx = 0) {
  if (lines.length === 0) throw new RangeError("Order has no items");
  if (!Number.isSafeInteger(deliveryFeeUgx) || deliveryFeeUgx < 0) throw new RangeError("Invalid delivery fee");
  let subtotal = 0;
  for (const l of lines) {
    if (!Number.isSafeInteger(l.unitPriceUgx) || l.unitPriceUgx < 0) throw new RangeError("Invalid price");
    if (!Number.isInteger(l.quantity) || l.quantity < 1 || l.quantity > MAX_QTY_PER_LINE) throw new RangeError("Invalid quantity");
    subtotal += l.unitPriceUgx * l.quantity;
  }
  return { subtotalUgx: subtotal, deliveryFeeUgx, totalUgx: subtotal + deliveryFeeUgx };
}

/** Human-friendly reference, no ambiguous characters (0/O, 1/I). */
export function newOrderReference(rand: (n: number) => number = (n) => Math.floor(Math.random() * n)): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let s = "";
  for (let i = 0; i < 6; i++) s += alphabet[rand(alphabet.length)];
  return `ORD-${s}`;
}
