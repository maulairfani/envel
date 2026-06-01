"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { cn } from "@/lib/utils";

/**
 * App frame: fixed sidebar on desktop (md+), a slide-in drawer on mobile with a
 * hamburger in a top bar. The same sidebar content is reused in both.
 */
export function AppShell({
  sidebar,
  children,
}: {
  sidebar: React.ReactNode;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  // Close the drawer whenever the route changes (nav link / chat selection).
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Lock background scroll while the drawer is open.
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <div className="flex h-dvh overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-border bg-sidebar md:block">
        {sidebar}
      </aside>

      {/* Mobile drawer + backdrop */}
      <div className={cn("fixed inset-0 z-50 md:hidden", !open && "pointer-events-none")}>
        <div
          onClick={() => setOpen(false)}
          className={cn(
            "absolute inset-0 bg-black/50 transition-opacity duration-200",
            open ? "opacity-100" : "opacity-0",
          )}
        />
        <aside
          className={cn(
            "absolute inset-y-0 left-0 w-72 max-w-[80%] border-r border-border bg-sidebar shadow-xl transition-transform duration-200",
            open ? "translate-x-0" : "-translate-x-full",
          )}
        >
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
            className="absolute right-3 top-3 z-10 rounded-md p-1.5 text-muted-foreground hover:bg-surface-2 hover:text-foreground"
          >
            <X className="size-5" />
          </button>
          {sidebar}
        </aside>
      </div>

      <main className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="flex items-center gap-3 border-b border-border px-4 py-2.5 md:hidden">
          <button
            type="button"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            className="-ml-1.5 rounded-md p-1.5 text-muted-foreground hover:bg-surface-2 hover:text-foreground"
          >
            <Menu className="size-5" />
          </button>
          <Logo />
        </header>
        <div className="min-h-0 flex-1">{children}</div>
      </main>
    </div>
  );
}
