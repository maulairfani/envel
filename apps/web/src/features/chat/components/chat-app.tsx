"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useThreads } from "../hooks/use-threads";
import { ThreadSidebar } from "./thread-sidebar";
import { ChatView } from "./chat-view";

/** Top-level chat experience: thread sidebar + active conversation. */
export function ChatApp() {
  // `view.key` controls ChatView remounts (reset useStream). It changes only on
  // explicit navigation (new chat / pick a thread) — NOT when a thread is
  // auto-created mid-stream, which would kill the in-flight response.
  const [view, setView] = useState<{ threadId: string | null; key: string }>({
    threadId: null,
    key: "new",
  });
  const [activeId, setActiveId] = useState<string | null>(null);
  const { threads, refresh } = useThreads();

  function newChat() {
    setView({ threadId: null, key: `new-${crypto.randomUUID()}` });
    setActiveId(null);
  }

  function selectThread(id: string) {
    setView({ threadId: id, key: id });
    setActiveId(id);
  }

  return (
    <AppShell
      sidebar={
        <ThreadSidebar
          threads={threads}
          activeId={activeId}
          onSelect={selectThread}
          onNew={newChat}
        />
      }
    >
      <ChatView
        key={view.key}
        threadId={view.threadId}
        onThreadCreated={(id) => {
          setActiveId(id); // highlight in sidebar; no remount
          void refresh();
        }}
      />
    </AppShell>
  );
}
