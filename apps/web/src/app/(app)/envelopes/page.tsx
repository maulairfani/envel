import { redirect } from "next/navigation";
import { getToken } from "@/features/auth/session";
import { getWorkspace, EnvelopeList, PeriodPicker } from "@/features/finance";
import { MoneyText } from "@/components/ui";
import { PageView } from "@/components/layout/page-view";
import { resolvePeriod } from "@/lib/period";

export default async function EnvelopesPage({
  searchParams,
}: {
  searchParams: Promise<{ period?: string }>;
}) {
  const token = await getToken();
  if (!token) redirect("/login");

  const period = resolvePeriod((await searchParams).period);

  let ws;
  try {
    ws = await getWorkspace(token, period);
  } catch {
    return (
      <PageView title="Envelopes">
        <p className="text-sm text-negative">Failed to load data from the server.</p>
      </PageView>
    );
  }

  const rta = ws.summary.ready_to_assign;

  return (
    <PageView title="Envelopes">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 px-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Period
          </div>
          <PeriodPicker period={period} basePath="/envelopes" />
        </div>
        <div className="sm:text-right">
          <div className="text-xs text-muted-foreground">Ready to assign</div>
          <MoneyText
            amount={rta}
            tone={rta < 0 ? "negative" : rta > 0 ? "positive" : "neutral"}
            className="text-lg"
          />
        </div>
      </div>
      <EnvelopeList groups={ws.envelope_groups} envelopes={ws.envelopes} />
    </PageView>
  );
}
