/** Shapes returned by the MCP `get_workspace` tool (see mcp-server get_workspace.py). */

export type AccountType = "cash" | "bank" | "ewallet" | "credit_card";
export type TargetType = "spend_monthly" | "save_monthly" | "save_total" | "save_by_date";

export interface Account {
  id: number;
  name: string;
  type: AccountType;
  balance: number;
}

export interface EnvelopeGroup {
  id: number;
  name: string;
  sort_order: number;
}

export interface Envelope {
  id: number;
  name: string;
  icon: string | null;
  group_id: number | null;
  target_type: TargetType | null;
  target_amount: number | null;
  target_date: string | null;
  assigned: number;
  activity: number;
  available: number;
}

export interface WorkspaceSummary {
  total_balance: number;
  total_available: number;
  ready_to_assign: number;
  is_balanced: boolean;
  is_overspent: boolean;
}

export interface Workspace {
  period: string;
  accounts: Account[];
  envelope_groups: EnvelopeGroup[];
  envelopes: Envelope[];
  summary: WorkspaceSummary;
  ready_to_assign: number;
}

export type TransactionType = "income" | "expense" | "transfer";

export interface Transaction {
  id: number;
  type: TransactionType;
  account_id: number | null;
  envelope_id: number | null;
  transfer_account_id: number | null;
  amount: number;
  date: string;
  payee: string | null;
  memo: string | null;
}

export interface TransactionPage {
  transactions: Transaction[];
  rowcount: number;
  has_more: boolean;
}
