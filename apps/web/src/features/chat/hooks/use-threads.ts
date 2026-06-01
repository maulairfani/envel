"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { Message } from "@langchain/langgraph-sdk";
import { createClient } from "../api/client";

export interface ThreadSummary {
  id: string;
  title: string;
}

function deriveTitle(values: unknown): string {
  const messages = (values as { messages?: Message[] } | null)?.messages;
  const firstHuman = messages?.find((m) => m.type === "human");
  if (firstHuman) {
    const text = typeof firstHuman.content === "string" ? firstHuman.content : "";
    if (text.trim()) return text.trim().slice(0, 60);
  }
  return "Percakapan baru";
}

/** List the current user's threads (owner-scoped server-side) for the sidebar. */
export function useThreads() {
  const client = useMemo(() => createClient(), []);
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const results = await client.threads.search({ limit: 50 });
      setThreads(
        results.map((t) => ({ id: t.thread_id, title: deriveTitle(t.values) })),
      );
    } catch {
      setThreads([]);
    } finally {
      setLoading(false);
    }
  }, [client]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { threads, loading, refresh };
}
