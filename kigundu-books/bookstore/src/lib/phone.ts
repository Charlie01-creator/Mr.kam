/**
 * Uganda phone numbers. Accepts 07XXXXXXXX, 7XXXXXXXX, 2567XXXXXXXX,
 * +2567XXXXXXXX, 00256..., with spaces, dashes or brackets.
 * Mobile: 7 + 8 digits. Landline: 3 or 4 + 8 digits (e.g. 0414XXXXXX / 0312XXXXXX).
 * Returns E.164 (+256...) or null. Format check only, not proof the number is live.
 */
export function normaliseUgPhone(input: string): string | null {
  let d = input.replace(/[\s\-().]/g, "");
  if (d.startsWith("+")) d = d.slice(1);
  if (!/^\d+$/.test(d)) return null;
  if (d.startsWith("00256")) d = d.slice(2);
  if (d.startsWith("256")) d = d.slice(3);
  else if (d.startsWith("0")) d = d.slice(1);
  if (!/^[347]\d{8}$/.test(d)) return null;
  return `+256${d}`;
}

export function whatsappLink(digitsOnly: string, text?: string): string | null {
  const n = normaliseUgPhone(digitsOnly);
  if (!n) return null;
  const q = text ? `?text=${encodeURIComponent(text)}` : "";
  return `https://wa.me/${n.slice(1)}${q}`;
}
