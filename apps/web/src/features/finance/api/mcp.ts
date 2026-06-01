import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { env } from "@/config/env";

/**
 * Call one MCP tool with the user's bearer and return its parsed result.
 * FastMCP may return the dict as structuredContent (possibly wrapped under
 * `result`) or as a JSON text block — handle all shapes.
 */
export async function callMcpTool<T>(
  token: string,
  name: string,
  args: Record<string, unknown> = {},
): Promise<T> {
  const transport = new StreamableHTTPClientTransport(new URL(env.mcpUrl), {
    requestInit: { headers: { Authorization: `Bearer ${token}` } },
  });
  const client = new Client({ name: "envel-web", version: "1.0.0" });
  try {
    await client.connect(transport);
    const result = (await client.callTool({ name, arguments: args })) as {
      structuredContent?: Record<string, unknown>;
      content?: Array<{ type: string; text?: string }>;
    };

    const sc = result.structuredContent;
    if (sc && typeof sc === "object") {
      if ("result" in sc && sc.result && typeof sc.result === "object") {
        return sc.result as T;
      }
      return sc as T;
    }
    const text = result.content?.find((c) => c.type === "text")?.text;
    if (text) return JSON.parse(text) as T;

    throw new Error(`Unexpected MCP result shape for ${name}`);
  } finally {
    await client.close();
  }
}
