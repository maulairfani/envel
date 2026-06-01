import { Client } from "@langchain/langgraph-sdk";

/** Absolute URL of our same-origin proxy. The SDK builds requests with
 *  `new URL()`, which rejects a relative base — so we prepend the origin. */
export function getApiUrl() {
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  return `${origin}/api/lg`;
}

/** Browser LangGraph client — talks to /api/lg, which injects the bearer from
 *  the httpOnly cookie. Cookies ride along automatically (same-origin). */
export function createClient() {
  return new Client({ apiUrl: getApiUrl() });
}

/** The single graph the agent exposes (see apps/agent/langgraph.json). */
export const ASSISTANT_ID = "envel";
