"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { SlidersHorizontal, ChevronDown, Check } from "lucide-react";
import { Input, Label } from "@/components/ui";
import { cn, focusRing } from "@/lib/utils";
import { TX_TYPES, parseTypes, parseIds } from "../lib/filters";
import type { Account, Envelope } from "../types";

const selectCls = cn(
  "h-9 w-full rounded-md border border-input bg-transparent px-2 text-sm text-foreground",
  "[&>option]:bg-surface [&>option]:text-foreground",
  focusRing,
);

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label className="px-0.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </Label>
      {children}
    </div>
  );
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        "h-9 rounded-md border px-3 text-sm transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-input text-muted-foreground hover:bg-surface-2 hover:text-foreground",
        focusRing,
      )}
    >
      {children}
    </button>
  );
}

/** Dropdown that allows selecting multiple options via checkboxes. */
function MultiSelect({
  label,
  allLabel,
  options,
  selected,
  onToggle,
}: {
  label: string;
  allLabel: string;
  options: { id: number; name: string }[];
  selected: number[];
  onToggle: (id: number) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onDown(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);

  const summary =
    selected.length === 0
      ? allLabel
      : selected.length === 1
        ? options.find((o) => o.id === selected[0])?.name ?? `${selected.length} selected`
        : `${selected.length} selected`;

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        aria-label={label}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className={cn(selectCls, "flex items-center justify-between gap-2 text-left")}
      >
        <span className={cn("truncate", selected.length === 0 && "text-muted-foreground")}>{summary}</span>
        <ChevronDown className={cn("size-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border border-border bg-surface p-1 shadow-md">
          {options.map((o) => {
            const active = selected.includes(o.id);
            return (
              <button
                key={o.id}
                type="button"
                onClick={() => onToggle(o.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm transition-colors hover:bg-surface-2",
                  active ? "text-foreground" : "text-muted-foreground",
                )}
              >
                <span className={cn(
                  "flex size-4 shrink-0 items-center justify-center rounded border",
                  active ? "border-primary bg-primary text-primary-foreground" : "border-input",
                )}>
                  {active && <Check className="size-3" />}
                </span>
                <span className="truncate">{o.name}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface TransactionFiltersProps {
  accounts: Account[];
  envelopes: Envelope[];
}

/** Expandable, URL-driven transaction filters: type, account, envelope, payee. */
export function TransactionFilters({ accounts, envelopes }: TransactionFiltersProps) {
  const router = useRouter();
  const params = useSearchParams();

  const types = parseTypes(params.get("type") ?? undefined);
  const accountIds = parseIds(params.get("account") ?? undefined);
  const envelopeIds = parseIds(params.get("envelope") ?? undefined);
  const q = params.get("q") ?? "";

  const count = types.length + accountIds.length + envelopeIds.length + (q ? 1 : 0);
  const [open, setOpen] = useState(count > 0);

  function toggleAccount(id: number) {
    const next = accountIds.includes(id)
      ? accountIds.filter((a) => a !== id)
      : [...accountIds, id];
    setParam("account", next.join(","));
  }

  function toggleType(value: string) {
    const next = types.includes(value as (typeof types)[number])
      ? types.filter((t) => t !== value)
      : [...types, value as (typeof types)[number]];
    setParam("type", next.join(","));
  }

  function toggleEnvelope(id: number) {
    const next = envelopeIds.includes(id)
      ? envelopeIds.filter((e) => e !== id)
      : [...envelopeIds, id];
    setParam("envelope", next.join(","));
  }

  // Local payee input, pushed to the URL after a short debounce.
  const [payee, setPayee] = useState(q);
  useEffect(() => setPayee(q), [q]);
  useEffect(() => {
    if (payee === q) return;
    const id = setTimeout(() => setParam("q", payee), 350);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payee]);

  function navigate(next: URLSearchParams) {
    const qs = next.toString();
    router.push(qs ? `/transactions?${qs}` : "/transactions");
  }

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    navigate(next);
  }

  function reset() {
    // Clear filters but keep the selected period.
    const next = new URLSearchParams();
    const period = params.get("period");
    if (period) next.set("period", period);
    navigate(next);
  }

  return (
    <div className="mb-5 rounded-lg border border-border bg-surface">
      <div className="flex items-center justify-between gap-2 px-4 py-3">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className={cn(
            "-mx-2 -my-1 flex items-center gap-2 rounded-md px-2 py-1 text-sm font-medium text-foreground transition-colors hover:text-foreground",
            focusRing,
          )}
          aria-expanded={open}
        >
          <SlidersHorizontal className="size-4 text-muted-foreground" />
          Filter
          {count > 0 && (
            <span className="rounded-full bg-primary px-1.5 text-xs font-medium text-primary-foreground">
              {count}
            </span>
          )}
          <ChevronDown className={cn("size-4 text-muted-foreground transition-transform", open && "rotate-180")} />
        </button>
        {count > 0 && (
          <button
            type="button"
            onClick={reset}
            className="text-xs font-medium text-primary hover:underline"
          >
            Reset
          </button>
        )}
      </div>

      {open && (
        <div className="space-y-4 border-t border-border p-4">
          <Field label="Type">
            <div className="flex flex-wrap gap-2">
              {TX_TYPES.map((t) => (
                <Chip key={t.value} active={types.includes(t.value)} onClick={() => toggleType(t.value)}>
                  {t.label}
                </Chip>
              ))}
            </div>
          </Field>

          <Field label="Account">
            <MultiSelect
              label="Account"
              allLabel="All accounts"
              options={accounts.map((a) => ({ id: a.id, name: a.name }))}
              selected={accountIds}
              onToggle={toggleAccount}
            />
          </Field>

          <Field label="Envelope">
            <MultiSelect
              label="Envelope"
              allLabel="All envelopes"
              options={envelopes.map((e) => ({ id: e.id, name: e.name }))}
              selected={envelopeIds}
              onToggle={toggleEnvelope}
            />
          </Field>

          <Field label="Search payee / memo">
            <Input
              type="search"
              aria-label="Search payee or memo"
              placeholder="Search payee or memo…"
              value={payee}
              onChange={(e) => setPayee(e.target.value)}
              className="h-9"
            />
          </Field>
        </div>
      )}
    </div>
  );
}
