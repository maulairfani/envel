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
    return NextResponse.redirect(new URL("/login", req.nextUrl.origin));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|brand).*)"],
};
