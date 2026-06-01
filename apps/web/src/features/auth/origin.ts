import type { NextRequest } from "next/server";

/**
 * The browser-facing origin of the request, honoring the reverse proxy's
 * forwarded headers. Inside the container `req.nextUrl.origin` is the internal
 * bind host (e.g. http://0.0.0.0:3000); the real origin is in
 * `X-Forwarded-Proto` + `X-Forwarded-Host` (or `Host`). Used for the OAuth
 * `redirect_uri` sent to the auth-server.
 */
export function externalOrigin(req: NextRequest): string {
  const proto =
    req.headers.get("x-forwarded-proto")?.split(",")[0].trim() ||
    req.nextUrl.protocol.replace(":", "");
  const host =
    req.headers.get("x-forwarded-host")?.split(",")[0].trim() ||
    req.headers.get("host") ||
    req.nextUrl.host;
  return `${proto}://${host}`;
}
