/**
 * Money helpers. Envel money is always an IDR integer (no decimals).
 */

const idr = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
});

const idrPlain = new Intl.NumberFormat("id-ID", { maximumFractionDigits: 0 });

/** "Rp1.250.000" */
export function formatIDR(amount: number): string {
  return idr.format(amount);
}

/** "1.250.000" — no currency symbol, for dense tables. */
export function formatIDRPlain(amount: number): string {
  return idrPlain.format(amount);
}

export type MoneyTone = "auto" | "neutral" | "positive" | "negative";

/** Resolve a tone from a signed amount when tone is "auto". */
export function resolveMoneyTone(amount: number, tone: MoneyTone): Exclude<MoneyTone, "auto"> {
  if (tone !== "auto") return tone;
  if (amount > 0) return "positive";
  if (amount < 0) return "negative";
  return "neutral";
}
