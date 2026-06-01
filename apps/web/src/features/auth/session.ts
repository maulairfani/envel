import { cookies } from "next/headers";
import { TOKEN_COOKIE } from "./constants";

/** Read the Envel token from the httpOnly cookie (server-side only). */
export async function getToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(TOKEN_COOKIE)?.value ?? null;
}

export async function isAuthenticated(): Promise<boolean> {
  return (await getToken()) !== null;
}
