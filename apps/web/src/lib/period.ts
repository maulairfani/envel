/** Budget period helpers. A period is "YYYY-MM". */

const PERIOD_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

export function isValidPeriod(p: string | undefined | null): p is string {
  return typeof p === "string" && PERIOD_RE.test(p);
}

export function currentPeriod(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

/** Resolve a (possibly invalid) input to a valid period, defaulting to now. */
export function resolvePeriod(p: string | undefined | null): string {
  return isValidPeriod(p) ? p : currentPeriod();
}

/** Shift a period by N months (negative = back). */
export function shiftPeriod(period: string, delta: number): string {
  const [y, m] = period.split("-").map(Number);
  const idx = (y * 12 + (m - 1)) + delta;
  const ny = Math.floor(idx / 12);
  const nm = (idx % 12) + 1;
  return `${ny}-${String(nm).padStart(2, "0")}`;
}

/** First and last day (inclusive) of a period's month, as ISO dates. */
export function periodRange(period: string): { date_from: string; date_to: string } {
  const [y, m] = period.split("-").map(Number);
  const lastDay = new Date(y, m, 0).getDate();
  return { date_from: `${period}-01`, date_to: `${period}-${String(lastDay).padStart(2, "0")}` };
}

const labelFmt = new Intl.DateTimeFormat("id-ID", { month: "long", year: "numeric" });

/** "2026-06" → "Juni 2026" */
export function formatPeriod(period: string): string {
  const [y, m] = period.split("-").map(Number);
  return labelFmt.format(new Date(y, m - 1, 1));
}
