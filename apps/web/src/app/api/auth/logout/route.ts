import { NextRequest, NextResponse } from "next/server";
import { TOKEN_COOKIE } from "@/features/auth/constants";

/** Clear the session cookie and bounce to the login page. */
export async function POST(req: NextRequest) {
  const res = NextResponse.redirect(new URL("/login", req.nextUrl.origin));
  res.cookies.delete(TOKEN_COOKIE);
  return res;
}
