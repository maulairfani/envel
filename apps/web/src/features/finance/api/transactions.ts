import { callMcpTool } from "./mcp";
import type { TransactionPage } from "../types";

export interface ReadTransactionsParams {
  envelope_id?: number;
  envelope_ids?: number[];
  account_id?: number;
  account_ids?: number[];
  type?: "income" | "expense" | "transfer";
  types?: ("income" | "expense" | "transfer")[];
  date_from?: string;
  date_to?: string;
  payee_contains?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

/** Read-path: MCP `read_transactions` (newest first, returns has_more). */
export function readTransactions(
  token: string,
  params: ReadTransactionsParams = {},
): Promise<TransactionPage> {
  return callMcpTool<TransactionPage>(token, "read_transactions", { ...params });
}
