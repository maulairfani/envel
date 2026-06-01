"use client";

import { useState } from "react";
import { ChevronRight, Check, X, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ToolCall } from "../types";

const statusIcon = {
  running: <Loader2 className="size-3.5 animate-spin text-muted-foreground" />,
  success: <Check className="size-3.5 text-positive" />,
  error: <X className="size-3.5 text-negative" />,
};

/** Collapsible view of one MCP tool call — transparency for the MCP client. */
export function ToolCallView({ call }: { call: ToolCall }) {
  const [open, setOpen] = useState(false);
  const hasDetail = call.args !== undefined || call.result !== undefined;

  return (
    <div className="overflow-hidden rounded-md border border-tool-border bg-tool text-xs">
      <button
        type="button"
        onClick={() => hasDetail && setOpen((v) => !v)}
        className={cn(
          "flex w-full items-center gap-2 px-3 py-2 text-left transition-colors",
          hasDetail && "hover:bg-surface-2",
        )}
      >
        {hasDetail ? (
          <ChevronRight className={cn("size-3.5 transition-transform", open && "rotate-90")} />
        ) : (
          <span className="size-3.5" />
        )}
        <span className="font-numeric font-medium text-foreground">{call.name}</span>
        <span className="ml-auto">{statusIcon[call.status]}</span>
      </button>
      {open && hasDetail && (
        <div className="space-y-2 border-t border-tool-border px-3 py-2">
          {call.args !== undefined && (
            <Detail label="args" value={call.args} />
          )}
          {call.result !== undefined && (
            <Detail label="result" value={call.result} />
          )}
        </div>
      )}
    </div>
  );
}

function Detail({ label, value }: { label: string; value: unknown }) {
  return (
    <div>
      <div className="mb-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <pre className="max-h-64 overflow-auto overscroll-contain whitespace-pre-wrap break-words rounded bg-surface-2/40 p-2 font-numeric text-[11px] leading-relaxed text-foreground/80">
        {typeof value === "string" ? value : JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}
