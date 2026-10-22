import { test } from "node:test";
import assert from "node:assert/strict";
import { formatUgx, isValidUgx } from "./money.ts";

test("formats UGX with thousands separators", () => {
  assert.equal(formatUgx(0), "UGX 0");
  assert.equal(formatUgx(25000), "UGX 25,000");
  assert.equal(formatUgx(1234567), "UGX 1,234,567");
});
test("rejects fractional amounts", () => {
  assert.throws(() => formatUgx(10.5), RangeError);
  assert.equal(isValidUgx(10.5), false);
  assert.equal(isValidUgx(-1), false);
});
