/**
 * Server-side environment config. Never import this into client components —
 * these values (and the token they guard) must stay on the server.
 */
export const env = {
  /** Auth-server base URL — used for the /authorize redirect and /token exchange. */
  authUrl: process.env.AUTH_URL ?? "http://localhost:9000",
  /** LangGraph agent base URL — used by the /api/lg proxy (slice 2). */
  agentUrl: process.env.AGENT_URL ?? "http://localhost:2024",
  /** Secure cookies only outside development. */
  isProd: process.env.NODE_ENV === "production",
};
