import { test } from "node:test";
import assert from "node:assert/strict";
import { normaliseUgPhone, whatsappLink } from "./phone.ts";

test("normalises local and international mobile formats", () => {
  for (const v of ["0772123456", "772123456", "+256772123456", "256772123456", "00256772123456", "0772 123 456", "(0772)-123-456"]) {
    assert.equal(normaliseUgPhone(v), "+256772123456", v);
  }
});
test("accepts landlines", () => assert.equal(normaliseUgPhone("0414 123456"), "+256414123456"));
test("rejects bad numbers", () => {
  for (const v of ["", "abc", "077212345", "07721234567", "+254712345678", "0172123456", "<script>"]) {
    assert.equal(normaliseUgPhone(v), null, v);
  }
});
test("whatsapp link", () => {
  assert.equal(whatsappLink("0772123456"), "https://wa.me/256772123456");
  assert.equal(whatsappLink("nope"), null);
});
