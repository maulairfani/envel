import { PageView } from "@/components/layout/page-view";

export default function DashboardsPage() {
  return (
    <PageView title="Dashboards">
      <div className="rounded-lg border border-dashed border-border p-8 text-center">
        <p className="text-sm text-muted-foreground">
          Coming soon — you'll be able to build your own dashboards with Grafana.
        </p>
      </div>
    </PageView>
  );
}
