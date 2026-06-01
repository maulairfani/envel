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
        <p className="text-sm text-negative">Gagal memuat data dari server.</p>
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
      <div className="mb-3 flex items-end justify-between gap-4">
        <div>
          <div className="mb-2 px-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Period
          </div>
          <PeriodPicker period={period} basePath="/transactions" />
        </div>
        <div className="flex gap-6 text-right">
          <div>
            <div className="text-xs text-muted-foreground">Masuk</div>
            <MoneyText amount={income} tone="positive" showSign className="text-lg" />
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Keluar</div>
            <MoneyText amount={-expense} tone="negative" className="text-lg" />
          </div>
        </div>
      </div>

      <TransactionFilters accounts={ws.accounts} envelopes={ws.envelopes} />

      {page.transactions.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {filtered
            ? "Tidak ada transaksi yang cocok dengan filter."
            : "Belum ada transaksi pada periode ini."}
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
