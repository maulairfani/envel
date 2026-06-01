export type ChatRole = "user" | "assistant";

export type ToolCallStatus = "running" | "success" | "error";

export interface ToolCall {
  id: string;
  /** Bare MCP tool name, e.g. "get_workspace". */
  name: string;
  args?: Record<string, unknown>;
  result?: unknown;
  status: ToolCallStatus;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  /** Tool calls emitted while producing an assistant turn. */
  toolCalls?: ToolCall[];
}
