"use client";

import { Plus, LogOut } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { ThreadSummary } from "../hooks/use-threads";

interface ThreadSidebarProps {
  threads: ThreadSummary[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export function ThreadSidebar({ threads, activeId, onSelect, onNew }: ThreadSidebarProps) {
  return (
    <div className="flex h-full flex-col gap-2 p-3">
      <div className="px-2 py-3">
        <Logo />
      </div>

      <Button variant="outline" className="justify-start gap-2" onClick={onNew}>
        <Plus /> Chat baru
      </Button>

      <nav className="mt-2 flex-1 space-y-0.5 overflow-y-auto">
        {threads.map((t) => (
          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className={cn(
              "block w-full truncate rounded-md px-3 py-2 text-left text-sm transition-colors",
              t.id === activeId
                ? "bg-surface-2 text-foreground"
                : "text-muted-foreground hover:bg-surface-2 hover:text-foreground",
            )}
            title={t.title}
          >
            {t.title}
          </button>
        ))}
      </nav>

      <form action="/api/auth/logout" method="post">
        <Button type="submit" variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
          <LogOut /> Keluar
        </Button>
      </form>
    </div>
  );
}
