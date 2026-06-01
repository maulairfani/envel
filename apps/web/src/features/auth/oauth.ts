import { env } from "@/config/env";

export interface TokenResult {
  token: string;
  expiresIn: number;
}

/**
 * Run the OAuth code flow server-to-server so the browser never leaves
 * chat.envel.dev: POST credentials to the auth-server's /login, read the
 * `code` off the redirect's Location header, then exchange it at /token.
 * Returns null on bad credentials or any failure.
 */
export async function exchangeCredentialsForToken(
  username: string,
  password: string,
  origin: string,
): Promise<TokenResult | null> {
  const redirectUri = new URL("/", origin).toString();

  const loginRes = await fetch(new URL("/login", env.authUrl), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password, redirect_uri: redirectUri, state: "" }),
    redirect: "manual",
  });

  // Success is a 3xx redirect to `${redirectUri}?code=...`; failure is 401.
  const location = loginRes.headers.get("location");
  if (!location) return null;

  let code: string | null = null;
  try {
    code = new URL(location).searchParams.get("code");
  } catch {
    return null;
  }
  if (!code) return null;

  const tokenRes = await fetch(new URL("/token", env.authUrl), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ code }),
  });
  if (!tokenRes.ok) return null;

  const data = (await tokenRes.json()) as { access_token?: string; expires_in?: number };
  if (!data.access_token) return null;

  return { token: data.access_token, expiresIn: data.expires_in ?? 3600 };
}
