import { test } from "node:test";
import assert from "node:assert/strict";
import { slugify } from "./slug.ts";

test("slugify", () => {
  assert.equal(slugify("Essentials of Applied Mathematics in Statistics & Numerical Methods"),
    "essentials-of-applied-mathematics-in-statistics-numerical-methods");
  assert.equal(slugify("  Café  "), "cafe");
});
