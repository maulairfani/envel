"use client";

import { useChatNav } from "@/features/chat/chat-nav";
import { ChatView } from "@/features/chat";

export default function ChatPage() {
  const { threadId, sessionKey, markCreated } = useChatNav();
  return <ChatView key={sessionKey} threadId={threadId} onThreadCreated={markCreated} />;
}
