import { NextRequest, NextResponse } from "next/server";
import { TOKEN_COOKIE, isPublicPath } from "@/features/auth/constants";

/**
 * Route guard (Next 16 renamed `middleware` → `proxy`). Anyone without a
 * session cookie hitting a protected page is sent into the OAuth flow.
 * Token validity is enforced downstream (agent verifies the JWT); this is UX.
 */
export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // API routes enforce their own auth (and return 401 JSON rather than an
  // HTML redirect that would break fetch/XHR callers like the LangGraph SDK).
  if (pathname.startsWith("/api/")) return NextResponse.next();

  if (isPublicPath(pathname)) return NextResponse.next();

  const token = req.cookies.get(TOKEN_COOKIE)?.value;
  if (!token) {
    // Next 16 validates the proxy redirect's Location with `new URL()`, so a
    // relative "/login" throws ERR_INVALID_URL → 500. Build an absolute URL,
    // but from the forwarded headers, not req.nextUrl.origin (that is the
    // internal bind host, 0.0.0.0:3000, behind nginx-proxy-manager).
    const proto = req.headers.get("x-forwarded-proto") ?? req.nextUrl.protocol.replace(":", "");
    const host = req.headers.get("x-forwarded-host") ?? req.headers.get("host") ?? req.nextUrl.host;
    return NextResponse.redirect(new URL("/login", `${proto}://${host}`), 307);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|brand).*)"],
};
