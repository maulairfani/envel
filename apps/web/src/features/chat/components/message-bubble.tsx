import { Sparkles } from "lucide-react";
import { Markdown } from "@/components/ui";
import { ToolCallView } from "./tool-call-view";
import type { ChatMessage } from "../types";

/**
 * One chat turn. User turns are right-aligned bubbles; assistant turns are
 * full-width with the Envel mark and any MCP tool calls inlined above the text.
 */
export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-chat-user px-4 py-2.5 text-sm text-chat-user-foreground">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <Sparkles className="size-4" />
      </div>
      <div className="min-w-0 flex-1 space-y-2 pt-0.5">
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="space-y-1.5">
            {message.toolCalls.map((call) => (
              <ToolCallView key={call.id} call={call} />
            ))}
          </div>
        )}
        {message.content && (
          <Markdown className="text-chat-agent-foreground">{message.content}</Markdown>
        )}
      </div>
    </div>
  );
}
