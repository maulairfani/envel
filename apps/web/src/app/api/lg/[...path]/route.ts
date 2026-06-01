import { NextRequest, NextResponse } from "next/server";
import { env } from "@/config/env";
import { getToken } from "@/features/auth/session";

/**
 * Reverse proxy: browser → /api/lg/* → LangGraph agent server.
 *
 * The Envel token lives in an httpOnly cookie the browser JS can't read, so we
 * inject it here as the Bearer the agent's custom auth expects. Responses are
 * streamed through untouched so SSE chat (streamMode: "messages") works.
 */

// Hop-by-hop / encoding headers we must not copy back verbatim.
const STRIP_RESPONSE_HEADERS = new Set([
  "content-encoding",
  "content-length",
  "transfer-encoding",
  "connection",
]);

async function handle(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const token = await getToken();
  if (!token) {
    return NextResponse.json({ error: "unauthenticated" }, { status: 401 });
  }

  const { path } = await ctx.params;
  const target = `${env.agentUrl}/${path.join("/")}${req.nextUrl.search}`;

  // Forward request headers minus cookie/host; carry the user's bearer instead.
  const headers = new Headers(req.headers);
  headers.delete("cookie");
  headers.delete("host");
  headers.delete("connection");
  headers.set("authorization", `Bearer ${token}`);

  const hasBody = req.method !== "GET" && req.method !== "HEAD";

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: req.method,
      headers,
      body: hasBody ? req.body : undefined,
      // Required by undici when streaming a request body.
      ...(hasBody ? { duplex: "half" } : {}),
      redirect: "manual",
    } as RequestInit);
  } catch {
    return NextResponse.json({ error: "agent_unreachable" }, { status: 502 });
  }

  const resHeaders = new Headers();
  upstream.headers.forEach((value, key) => {
    if (!STRIP_RESPONSE_HEADERS.has(key.toLowerCase())) resHeaders.set(key, value);
  });

  // Pass the upstream stream straight through (no buffering → SSE stays live).
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: resHeaders,
  });
}

export {
  handle as GET,
  handle as POST,
  handle as PUT,
  handle as PATCH,
  handle as DELETE,
  handle as OPTIONS,
};
