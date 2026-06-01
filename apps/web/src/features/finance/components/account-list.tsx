import { Landmark, Wallet, Banknote, CreditCard, type LucideIcon } from "lucide-react";
import { Card, MoneyText } from "@/components/ui";
import type { Account, AccountType } from "../types";

const ICON: Record<AccountType, LucideIcon> = {
  bank: Landmark,
  ewallet: Wallet,
  cash: Banknote,
  credit_card: CreditCard,
};

const TYPE_LABEL: Record<AccountType, string> = {
  bank: "Bank",
  ewallet: "E-wallet",
  cash: "Cash",
  credit_card: "Kartu kredit",
};

export function AccountList({ accounts }: { accounts: Account[] }) {
  if (accounts.length === 0) {
    return <p className="text-sm text-muted-foreground">Belum ada akun.</p>;
  }
  return (
    <div className="space-y-2">
      {accounts.map((a) => {
        const Icon = ICON[a.type] ?? Wallet;
        return (
          <Card key={a.id} className="flex items-center gap-3 p-4">
            <div className="flex size-9 items-center justify-center rounded-md bg-surface-2 text-muted-foreground">
              <Icon className="size-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium">{a.name}</div>
              <div className="text-xs text-muted-foreground">{TYPE_LABEL[a.type] ?? a.type}</div>
            </div>
            <MoneyText amount={a.balance} tone="auto" className="text-sm" />
          </Card>
        );
      })}
    </div>
  );
}
