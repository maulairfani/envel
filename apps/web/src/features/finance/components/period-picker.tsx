"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { currentPeriod } from "@/lib/period";
import { cn, focusRing } from "@/lib/utils";

const MONTHS = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

const selectCls = cn(
  "h-9 rounded-md border border-input bg-transparent px-2 text-sm text-foreground",
  "[&>option]:bg-surface [&>option]:text-foreground",
  focusRing,
);

/** Direct month + year pickers; navigates to ?period=YYYY-MM on change. */
export function PeriodPicker({ period, basePath }: { period: string; basePath: string }) {
  const router = useRouter();
  const params = useSearchParams();
  const [year, month] = period.split("-").map(Number);

  // Single year for now; include the selected year if it ever differs.
  const years = Array.from(new Set([2026, year]));

  // Preserve any other active query params (e.g. transaction filters).
  const push = (period?: string) => {
    const next = new URLSearchParams(params.toString());
    if (period) next.set("period", period);
    else next.delete("period");
    const qs = next.toString();
    router.push(qs ? `${basePath}?${qs}` : basePath);
  };

  const go = (y: number, m: number) => push(`${y}-${String(m).padStart(2, "0")}`);

  const isCurrent = period === currentPeriod();

  return (
    <div className="flex items-center gap-2">
      <select
        aria-label="Bulan"
        value={month}
        onChange={(e) => go(year, Number(e.target.value))}
        className={selectCls}
      >
        {MONTHS.map((name, i) => (
          <option key={i} value={i + 1}>
            {name}
          </option>
        ))}
      </select>
      <select
        aria-label="Tahun"
        value={year}
        onChange={(e) => go(Number(e.target.value), month)}
        className={selectCls}
      >
        {years.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
      {!isCurrent && (
        <button
          type="button"
          onClick={() => push()}
          className="text-xs font-medium text-primary hover:underline"
        >
          Bulan ini
        </button>
      )}
    </div>
  );
}
