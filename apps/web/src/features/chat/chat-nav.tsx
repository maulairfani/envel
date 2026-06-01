"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

interface ChatNavState {
  /** Active thread id (null = unsaved new chat). */
  threadId: string | null;
  /** Remount key for ChatView — changes only on explicit navigation. */
  sessionKey: string;
  /** Bumped to ask the sidebar to refetch its thread list. */
  threadsVersion: number;
  newChat: () => void;
  selectThread: (id: string) => void;
  /** A thread was auto-created mid-stream: highlight it, refresh list, NO remount. */
  markCreated: (id: string) => void;
  refreshThreads: () => void;
}

const Ctx = createContext<ChatNavState | null>(null);

export function ChatNavProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [threadId, setThreadId] = useState<string | null>(null);
  const [sessionKey, setSessionKey] = useState("new");
  const [threadsVersion, setThreadsVersion] = useState(0);

  const newChat = useCallback(() => {
    setThreadId(null);
    setSessionKey(crypto.randomUUID());
    router.push("/");
  }, [router]);

  const selectThread = useCallback(
    (id: string) => {
      setThreadId(id);
      setSessionKey(id);
      router.push("/");
    },
    [router],
  );

  const markCreated = useCallback((id: string) => {
    setThreadId(id); // keep sessionKey → ChatView stays mounted (stream survives)
    setThreadsVersion((v) => v + 1);
  }, []);

  const refreshThreads = useCallback(() => setThreadsVersion((v) => v + 1), []);

  const value = useMemo(
    () => ({ threadId, sessionKey, threadsVersion, newChat, selectThread, markCreated, refreshThreads }),
    [threadId, sessionKey, threadsVersion, newChat, selectThread, markCreated, refreshThreads],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useChatNav() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useChatNav must be used within ChatNavProvider");
  return ctx;
}
