/** All money is whole UGX integers. Never floats. */
export function isValidUgx(n: unknown): n is number {
  return typeof n === "number" && Number.isSafeInteger(n) && n >= 0;
}

export function formatUgx(amount: number): string {
  if (!Number.isSafeInteger(amount)) throw new RangeError("Amount must be a whole number of UGX");
  const sign = amount < 0 ? "-" : "";
  return `${sign}UGX ${Math.abs(amount).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`;
}
