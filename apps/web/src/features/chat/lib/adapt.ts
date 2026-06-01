import type { Message } from "@langchain/langgraph-sdk";
import type { ChatMessage, ToolCall } from "../types";

/** Flatten LangChain message content (string or content blocks) to text. */
function toText(content: Message["content"]): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .map((block) => (block.type === "text" ? block.text : ""))
    .join("");
}

/**
 * Convert the LangGraph message stream into our display model: human turns,
 * assistant turns, and assistant tool calls hydrated with their results
 * (matched from the corresponding `tool` messages by tool_call_id).
 */
export function toChatMessages(messages: Message[]): ChatMessage[] {
  const toolResults = new Map<string, unknown>();
  for (const m of messages) {
    if (m.type === "tool") {
      const id = (m as { tool_call_id?: string }).tool_call_id;
      if (id) toolResults.set(id, m.content);
    }
  }

  const out: ChatMessage[] = [];
  for (const m of messages) {
    if (m.type === "human") {
      out.push({ id: m.id ?? `u-${out.length}`, role: "user", content: toText(m.content) });
    } else if (m.type === "ai") {
      const rawCalls = (m as { tool_calls?: Array<{ id?: string; name: string; args?: Record<string, unknown> }> })
        .tool_calls ?? [];
      const toolCalls: ToolCall[] = rawCalls.map((tc, i) => {
        const id = tc.id ?? `${m.id ?? "ai"}-tc-${i}`;
        const hasResult = tc.id ? toolResults.has(tc.id) : false;
        return {
          id,
          name: tc.name,
          args: tc.args,
          result: tc.id ? toolResults.get(tc.id) : undefined,
          status: hasResult ? "success" : "running",
        };
      });
      out.push({
        id: m.id ?? `a-${out.length}`,
        role: "assistant",
        content: toText(m.content),
        toolCalls: toolCalls.length ? toolCalls : undefined,
      });
    }
    // "tool" and "system" messages are folded in / ignored for display.
  }
  return out;
}
