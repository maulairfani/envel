/**
 * Pure auth constants — safe to import anywhere, including proxy.ts
 * (no next/headers, no server-only deps).
 */
export const TOKEN_COOKIE = "envel_token";

/** Paths reachable without a session. */
export const PUBLIC_PATHS = ["/login", "/api/auth", "/styleguide"];

export function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}
