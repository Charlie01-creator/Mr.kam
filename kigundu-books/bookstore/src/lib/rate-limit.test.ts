import { test } from "node:test";
import assert from "node:assert/strict";
import { rateLimit } from "./rate-limit.ts";

test("blocks after limit and resets after window", () => {
  const k = "t1";
  assert.equal(rateLimit(k, 2, 1000, 0).ok, true);
  assert.equal(rateLimit(k, 2, 1000, 1).ok, true);
  assert.equal(rateLimit(k, 2, 1000, 2).ok, false);
  assert.equal(rateLimit(k, 2, 1000, 1001).ok, true);
});
