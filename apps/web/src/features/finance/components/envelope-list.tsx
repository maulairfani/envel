import { Card, MoneyText } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { Envelope, EnvelopeGroup } from "../types";

function EnvelopeRow({ e }: { e: Envelope }) {
  const pct =
    e.target_amount && e.target_amount > 0
      ? Math.max(0, Math.min(100, Math.round((e.available / e.target_amount) * 100)))
      : null;
  const over = e.available < 0;

  return (
    <div className="flex flex-col gap-1.5 px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <span className="truncate text-sm font-medium">{e.name}</span>
        <MoneyText amount={e.available} tone={over ? "negative" : "neutral"} className="text-sm" />
      </div>
      {pct !== null && (
        <div className="h-1.5 overflow-hidden rounded-full bg-surface-2">
          <div
            className={cn("h-full rounded-full", over ? "bg-negative" : "bg-primary")}
            style={{ width: `${over ? 100 : pct}%` }}
          />
        </div>
      )}
    </div>
  );
}

export function EnvelopeList({
  groups,
  envelopes,
}: {
  groups: EnvelopeGroup[];
  envelopes: Envelope[];
}) {
  if (envelopes.length === 0) {
    return <p className="text-sm text-muted-foreground">Belum ada envelope.</p>;
  }

  const sections = [
    ...groups.map((g) => ({ id: g.id, name: g.name })),
    { id: null as number | null, name: "Lainnya" },
  ]
    .map((s) => ({ ...s, items: envelopes.filter((e) => e.group_id === s.id) }))
    .filter((s) => s.items.length > 0);

  return (
    <div className="space-y-6">
      {sections.map((s) => (
        <section key={s.id ?? "none"}>
          <h2 className="mb-2 px-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {s.name}
          </h2>
          <Card className="divide-y divide-border p-0">
            {s.items.map((e) => (
              <EnvelopeRow key={e.id} e={e} />
            ))}
          </Card>
        </section>
      ))}
    </div>
  );
}
