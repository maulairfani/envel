import { NextRequest, NextResponse } from "next/server";
import { env } from "@/config/env";
import { TOKEN_COOKIE } from "@/features/auth/constants";
import { exchangeCredentialsForToken } from "@/features/auth/oauth";

/**
 * Native login: accept the credentials form, exchange them for an Envel token
 * server-side, and drop it in an httpOnly cookie. No browser redirect to the
 * auth-server — the user stays on chat.envel.dev.
 */
export async function POST(req: NextRequest) {
  const origin = req.nextUrl.origin;
  const form = await req.formData();
  const username = String(form.get("username") ?? "").trim();
  const password = String(form.get("password") ?? "");

  const fail = () => NextResponse.redirect(new URL("/login?error=invalid", origin), 303);

  if (!username || !password) return fail();

  let result;
  try {
    result = await exchangeCredentialsForToken(username, password, origin);
  } catch {
    return NextResponse.redirect(new URL("/login?error=unavailable", origin), 303);
  }
  if (!result) return fail();

  const res = NextResponse.redirect(new URL("/", origin), 303);
  res.cookies.set(TOKEN_COOKIE, result.token, {
    httpOnly: true,
    secure: env.isProd,
    sameSite: "lax",
    path: "/",
    maxAge: result.expiresIn,
  });
  return res;
}
