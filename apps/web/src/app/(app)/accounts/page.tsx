import { redirect } from "next/navigation";
import { getToken } from "@/features/auth/session";
import { getWorkspace, AccountList } from "@/features/finance";
import { MoneyText } from "@/components/ui";
import { PageView } from "@/components/layout/page-view";

export default async function AccountsPage() {
  const token = await getToken();
  if (!token) redirect("/login");

  let ws;
  try {
    ws = await getWorkspace(token);
  } catch {
    return (
      <PageView title="Accounts">
        <p className="text-sm text-negative">Failed to load data from the server.</p>
      </PageView>
    );
  }

  return (
    <PageView
      title="Accounts"
      action={
        <div className="text-right">
          <div className="text-xs text-muted-foreground">Total balance</div>
          <MoneyText amount={ws.summary.total_balance} tone="auto" className="text-lg" />
        </div>
      }
    >
      <AccountList accounts={ws.accounts} />
    </PageView>
  );
}
