import { NextResponse } from "next/server";
import { TOKEN_COOKIE } from "@/features/auth/constants";

/** Clear the session cookie and bounce to the login page. */
export async function POST() {
  // Relative Location so the browser resolves against the public origin
  // (chat.envel.dev), not the container's internal bind host.
  const res = new NextResponse(null, { status: 303, headers: { Location: "/login" } });
  res.cookies.delete(TOKEN_COOKIE);
  return res;
}
