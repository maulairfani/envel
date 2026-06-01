import { callMcpTool } from "./mcp";
import type { Workspace } from "../types";

/**
 * Read-path: call the MCP `get_workspace` tool directly (no LLM), passing the
 * user's token as the bearer the MCP server introspects to resolve their DB.
 */
export function getWorkspace(token: string, period?: string): Promise<Workspace> {
  return callMcpTool<Workspace>(token, "get_workspace", period ? { period } : {});
}
