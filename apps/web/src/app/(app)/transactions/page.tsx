import { redirect } from "next/navigation";
import { getToken } from "@/features/auth/session";
import {
  getWorkspace,
  readTransactions,
  parseTransactionParams,
  activeFilterCount,
  TransactionList,
  TransactionFilters,
  PeriodPicker,
  type TransactionSearchParams,
} from "@/features/finance";
import { MoneyText } from "@/components/ui";
import { PageView } from "@/components/layout/page-view";
import { resolvePeriod } from "@/lib/period";

export default async function TransactionsPage({
  searchParams,
}: {
  searchParams: Promise<TransactionSearchParams>;
}) {
  const token = await getToken();
  if (!token) redirect("/login");

  const sp = await searchParams;
  const period = resolvePeriod(sp.period);

  let ws, page;
  try {
    [ws, page] = await Promise.all([
      getWorkspace(token),
      readTransactions(token, parseTransactionParams(sp, period)),
    ]);
  } catch {
    return (
      <PageView title="Transactions">
        <p className="text-sm text-negative">Failed to load data from the server.</p>
      </PageView>
    );
  }

  const accountNames = Object.fromEntries(ws.accounts.map((a) => [a.id, a.name]));
  const envelopeNames = Object.fromEntries(ws.envelopes.map((e) => [e.id, e.name]));
  const filtered = activeFilterCount(sp) > 0;

  // Aggregate over the transactions currently shown.
  const income = page.transactions.reduce((s, t) => (t.type === "income" ? s + t.amount : s), 0);
  const expense = page.transactions.reduce((s, t) => (t.type === "expense" ? s + t.amount : s), 0);

  return (
    <PageView title="Transactions">
      <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 px-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Period
          </div>
          <PeriodPicker period={period} basePath="/transactions" />
        </div>
        {/* Desktop: aggregate sits top-right next to the period picker. */}
        <div className="hidden gap-6 text-right sm:flex">
          <div>
            <div className="text-xs text-muted-foreground">In</div>
            <MoneyText amount={income} tone="positive" showSign className="text-lg" />
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Out</div>
            <MoneyText amount={-expense} tone="negative" className="text-lg" />
          </div>
        </div>
      </div>

      <TransactionFilters accounts={ws.accounts} envelopes={ws.envelopes} />

      {/* Mobile: aggregate sits below the filter, above the list. */}
      <div className="mb-3 flex gap-6 sm:hidden">
        <div>
          <div className="text-xs text-muted-foreground">In</div>
          <MoneyText amount={income} tone="positive" showSign className="text-lg" />
        </div>
        <div>
          <div className="text-xs text-muted-foreground">Out</div>
          <MoneyText amount={-expense} tone="negative" className="text-lg" />
        </div>
      </div>

      {page.transactions.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {filtered
            ? "No transactions match the filter."
            : "No transactions yet for this period."}
        </p>
      ) : (
        <TransactionList
          transactions={page.transactions}
          accountNames={accountNames}
          envelopeNames={envelopeNames}
        />
      )}
    </PageView>
  );
}
