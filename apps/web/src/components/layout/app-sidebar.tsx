"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import {
  Plus,
  LogOut,
  Wallet,
  Landmark,
  LayoutDashboard,
  ArrowLeftRight,
  type LucideIcon,
} from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui";
import { cn } from "@/lib/utils";
import { useChatNav } from "@/features/chat/chat-nav";
import { useThreads } from "@/features/chat/hooks/use-threads";

const NAV: { href: string; label: string; icon: LucideIcon }[] = [
  { href: "/envelopes", label: "Envelopes", icon: Wallet },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/accounts", label: "Accounts", icon: Landmark },
  { href: "/dashboards", label: "Dashboards", icon: LayoutDashboard },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { threadId, newChat, selectThread, threadsVersion } = useChatNav();
  const { threads, refresh } = useThreads();

  // Refetch the thread list when a thread is created/changed elsewhere.
  useEffect(() => {
    void refresh();
  }, [threadsVersion, refresh]);

  return (
    <div className="flex h-full flex-col gap-1 p-3">
      <div className="px-2 py-3">
        <Logo />
      </div>

      <Button variant="outline" className="justify-start gap-2" onClick={newChat}>
        <Plus /> Chat baru
      </Button>

      <nav className="mt-2 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-surface-2 text-foreground"
                  : "text-muted-foreground hover:bg-surface-2 hover:text-foreground",
              )}
            >
              <Icon className="size-4" /> {label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-4 flex-1 overflow-y-auto">
        <p className="px-3 pb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Riwayat
        </p>
        <div className="space-y-0.5">
          {threads.map((t) => {
            const active = pathname === "/" && t.id === threadId;
            return (
              <button
                key={t.id}
                onClick={() => selectThread(t.id)}
                title={t.title}
                className={cn(
                  "block w-full truncate rounded-md px-3 py-2 text-left text-sm transition-colors",
                  active
                    ? "bg-surface-2 text-foreground"
                    : "text-muted-foreground hover:bg-surface-2 hover:text-foreground",
                )}
              >
                {t.title}
              </button>
            );
          })}
        </div>
      </div>

      <form action="/api/auth/logout" method="post">
        <Button type="submit" variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
          <LogOut /> Keluar
        </Button>
      </form>
    </div>
  );
}
