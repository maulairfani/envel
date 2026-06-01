import type { ReadTransactionsParams } from "../api/transactions";
import type { TransactionType } from "../types";
import { periodRange } from "@/lib/period";

/** Raw query params for the transactions page (all optional, all strings). */
export interface TransactionSearchParams {
  period?: string;
  type?: string;
  account?: string;
  envelope?: string;
  q?: string;
}

export const TX_TYPES: { value: TransactionType; label: string }[] = [
  { value: "expense", label: "Expense" },
  { value: "income", label: "Income" },
  { value: "transfer", label: "Transfer" },
];

const TYPES = new Set<TransactionType>(["income", "expense", "transfer"]);

/** Parse a comma-separated `type` query param into a deduped, valid list. */
export function parseTypes(raw: string | undefined): TransactionType[] {
  if (!raw) return [];
  const seen = new Set<TransactionType>();
  for (const v of raw.split(",")) {
    const t = v.trim();
    if (TYPES.has(t as TransactionType)) seen.add(t as TransactionType);
  }
  return [...seen];
}

/** Parse page query params into a validated MCP read_transactions request. */
export function parseTransactionParams(
  sp: TransactionSearchParams,
  period: string,
  limit = 100,
): ReadTransactionsParams {
  const params: ReadTransactionsParams = { limit, ...periodRange(period) };

  const types = parseTypes(sp.type);
  if (types.length) params.types = types;

  const accountIds = parseIds(sp.account);
  if (accountIds.length) params.account_ids = accountIds;

  const envelopeIds = parseIds(sp.envelope);
  if (envelopeIds.length) params.envelope_ids = envelopeIds;

  const q = sp.q?.trim();
  if (q) params.search = q;

  return params;
}

/** Parse a comma-separated id query param into a deduped, positive int list. */
export function parseIds(raw: string | undefined): number[] {
  if (!raw) return [];
  const seen = new Set<number>();
  for (const v of raw.split(",")) {
    const n = Number(v.trim());
    if (Number.isInteger(n) && n > 0) seen.add(n);
  }
  return [...seen];
}

/** Count of active filters (period is not a filter — it's the base scope). */
export function activeFilterCount(sp: TransactionSearchParams): number {
  return (
    parseTypes(sp.type).length +
    parseIds(sp.account).length +
    parseIds(sp.envelope).length +
    (sp.q?.trim() ? 1 : 0)
  );
}
