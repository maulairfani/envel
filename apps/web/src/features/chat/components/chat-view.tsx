"use client";

import { useEffect, useMemo, useRef } from "react";
import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { ASSISTANT_ID, getApiUrl } from "../api/client";
import { toChatMessages } from "../lib/adapt";
import { MessageBubble } from "./message-bubble";
import { ChatComposer } from "./chat-composer";

interface ChatViewProps {
  threadId: string | null;
  onThreadCreated?: (threadId: string) => void;
}

export function ChatView({ threadId, onThreadCreated }: ChatViewProps) {
  const stream = useStream<{ messages: Message[] }>({
    apiUrl: getApiUrl(),
    assistantId: ASSISTANT_ID,
    messagesKey: "messages",
    threadId: threadId ?? undefined,
    onThreadId: (id) => onThreadCreated?.(id),
    reconnectOnMount: true,
  });

  const messages = useMemo(() => toChatMessages(stream.messages), [stream.messages]);

  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stream.messages]);

  function send(text: string) {
    stream.submit({ messages: [{ type: "human", content: text }] });
  }

  const empty = messages.length === 0;

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        {empty ? (
          <div className="flex h-full items-center justify-center px-6 text-center">
            <div className="space-y-2">
              <p className="text-lg font-semibold">Halo 👋</p>
              <p className="max-w-sm text-sm text-muted-foreground">
                Mau atur budget, catat pengeluaran, atau lihat sisa amplop? Tanya aja.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            {stream.error != null && (
              <p className="text-sm text-negative">
                Terjadi kesalahan saat menghubungi agent. Coba lagi.
              </p>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
      <ChatComposer onSend={send} onStop={stream.stop} isLoading={stream.isLoading} />
    </div>
  );
}
