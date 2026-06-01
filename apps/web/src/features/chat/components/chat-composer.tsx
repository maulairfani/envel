"use client";

import { useRef, useState } from "react";
import { ArrowUp, Square } from "lucide-react";
import { Button } from "@/components/ui";
import { cn } from "@/lib/utils";

interface ChatComposerProps {
  onSend: (text: string) => void;
  onStop?: () => void;
  isLoading?: boolean;
}

export function ChatComposer({ onSend, onStop, isLoading = false }: ChatComposerProps) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  function autoGrow() {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }

  function send() {
    const text = value.trim();
    if (!text || isLoading) return;
    onSend(text);
    setValue("");
    requestAnimationFrame(autoGrow);
  }

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-xl border border-border bg-surface p-2">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            autoGrow();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          rows={1}
          placeholder="Tanya apa aja soal budget kamu…"
          className={cn(
            "max-h-[200px] flex-1 resize-none bg-transparent px-2 py-1.5 text-sm",
            "placeholder:text-muted-foreground focus:outline-none",
          )}
        />
        {isLoading ? (
          <Button size="icon" variant="secondary" onClick={onStop} aria-label="Stop">
            <Square className="fill-current" />
          </Button>
        ) : (
          <Button size="icon" onClick={send} disabled={!value.trim()} aria-label="Kirim">
            <ArrowUp />
          </Button>
        )}
      </div>
    </div>
  );
}
