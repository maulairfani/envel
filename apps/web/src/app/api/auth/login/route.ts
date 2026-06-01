import { NextRequest, NextResponse } from "next/server";
import { env } from "@/config/env";
import { TOKEN_COOKIE } from "@/features/auth/constants";
import { exchangeCredentialsForToken } from "@/features/auth/oauth";
import { externalOrigin } from "@/features/auth/origin";

/**
 * Native login: accept the credentials form, exchange them for an Envel token
 * server-side, and drop it in an httpOnly cookie. No browser redirect to the
 * auth-server — the user stays on chat.envel.dev.
 */
/**
 * 303 redirect with a *relative* Location so the browser resolves it against
 * the address-bar origin (chat.envel.dev). Behind a proxy, the server's own
 * `nextUrl.origin` is the internal bind host (0.0.0.0:3000) — never send that.
 */
function seeOther(path: string): NextResponse {
  return new NextResponse(null, { status: 303, headers: { Location: path } });
}

export async function POST(req: NextRequest) {
  const origin = externalOrigin(req);
  const form = await req.formData();
  const username = String(form.get("username") ?? "").trim();
  const password = String(form.get("password") ?? "");

  const fail = () => seeOther("/login?error=invalid");

  if (!username || !password) return fail();

  let result;
  try {
    result = await exchangeCredentialsForToken(username, password, origin);
  } catch {
    return seeOther("/login?error=unavailable");
  }
  if (!result) return fail();

  const res = seeOther("/");
  res.cookies.set(TOKEN_COOKIE, result.token, {
    httpOnly: true,
    secure: env.isProd,
    sameSite: "lax",
    path: "/",
    maxAge: result.expiresIn,
  });
  return res;
}
