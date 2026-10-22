import { z } from "zod";
import { normaliseUgPhone } from "./phone.ts";
import { MAX_QTY_PER_LINE } from "./order-math.ts";

const phone = z.string().trim().transform((v, ctx) => {
  const n = normaliseUgPhone(v);
  if (!n) { ctx.addIssue({ code: "custom", message: "Enter a valid Uganda phone number, e.g. 0772 123 456" }); return z.NEVER; }
  return n;
});
const optionalEmail = z.string().trim().email().max(254).optional().or(z.literal("").transform(() => undefined));

export const orderSchema = z.object({
  customerName: z.string().trim().min(2).max(100),
  phone,
  email: optionalEmail,
  fulfilment: z.enum(["DELIVERY", "COLLECTION"]),
  deliveryZoneId: z.string().cuid().optional(),
  address: z.string().trim().max(300).optional(),
  notes: z.string().trim().max(500).optional(),
  items: z.array(z.object({
    bookId: z.string().cuid(),
    quantity: z.number().int().min(1).max(MAX_QTY_PER_LINE),
  })).min(1).max(20),
  // Honeypot: real users never fill this.
  website: z.string().max(0).optional(),
}).refine((o) => o.fulfilment !== "DELIVERY" || (o.address && o.deliveryZoneId), {
  message: "Delivery needs an address and a delivery area", path: ["address"],
});

export const enquirySchema = z.object({
  name: z.string().trim().min(2).max(100),
  phone: phone.optional().or(z.literal("").transform(() => undefined)),
  email: optionalEmail,
  message: z.string().trim().min(10).max(2000),
  website: z.string().max(0).optional(),
}).refine((o) => o.phone || o.email, { message: "Give a phone number or an email so we can reply", path: ["phone"] });
