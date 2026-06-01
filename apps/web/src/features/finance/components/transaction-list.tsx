import { Card, MoneyText } from "@/components/ui";
import type { Transaction } from "../types";

const dateFmt = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function formatDate(iso: string) {
  const [y, m, d] = iso.split("-").map(Number);
  return dateFmt.format(new Date(y, (m ?? 1) - 1, d ?? 1));
}

interface TransactionListProps {
  transactions: Transaction[];
  accountNames: Record<number, string>;
  envelopeNames: Record<number, string>;
}

export function TransactionList({
  transactions,
  accountNames,
  envelopeNames,
}: TransactionListProps) {
  if (transactions.length === 0) {
    return <p className="text-sm text-muted-foreground">Belum ada transaksi.</p>;
  }

  // Group consecutive transactions by date (already sorted newest-first).
  const groups: { date: string; items: Transaction[] }[] = [];
  for (const t of transactions) {
    const last = groups[groups.length - 1];
    if (last && last.date === t.date) last.items.push(t);
    else groups.push({ date: t.date, items: [t] });
  }

  return (
    <div className="space-y-6">
      {groups.map((g) => (
        <section key={g.date}>
          <h2 className="mb-2 px-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {formatDate(g.date)}
          </h2>
          <Card className="divide-y divide-border p-0">
            {g.items.map((t) => (
              <Row
                key={t.id}
                t={t}
                accountNames={accountNames}
                envelopeNames={envelopeNames}
              />
            ))}
          </Card>
        </section>
      ))}
    </div>
  );
}

function Row({
  t,
  accountNames,
  envelopeNames,
}: {
  t: Transaction;
  accountNames: Record<number, string>;
  envelopeNames: Record<number, string>;
}) {
  const acct = (id: number | null) => (id != null ? accountNames[id] ?? "Akun" : "Akun");

  let subtitle: string;
  if (t.type === "transfer") {
    subtitle = `${acct(t.account_id)} → ${acct(t.transfer_account_id)}`;
  } else if (t.type === "income") {
    subtitle = acct(t.account_id);
  } else {
    subtitle = t.envelope_id != null ? envelopeNames[t.envelope_id] ?? "Envelope" : acct(t.account_id);
  }

  // Title = "Memo - Payee" (whichever exist). If neither, fall back to the
  // subtitle so the row never shows an empty or placeholder line.
  const primary = [t.memo, t.payee].filter(Boolean).join(" - ");
  const title = primary || subtitle;
  const showSubtitle = primary.length > 0;

  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3">
      <div className="min-w-0">
        <div className="truncate text-sm font-medium">{title}</div>
        {showSubtitle && (
          <div className="truncate text-xs text-muted-foreground">{subtitle}</div>
        )}
      </div>
      {t.type === "expense" ? (
        <MoneyText amount={-t.amount} tone="negative" className="text-sm" />
      ) : t.type === "income" ? (
        <MoneyText amount={t.amount} tone="positive" showSign className="text-sm" />
      ) : (
        <MoneyText amount={t.amount} tone="neutral" className="text-sm" />
      )}
    </div>
  );
}
