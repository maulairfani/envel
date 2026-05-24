"""
Auth server minimal untuk MCP — OAuth 2.1 + JWT HS256, multi-user.

Endpoint (semua dibutuhkan Claude saat connect):
  GET  /.well-known/oauth-authorization-server  → discovery
  POST /register                                → dynamic client registration
  GET  /authorize                               → form login HTML
  POST /login                                   → verify password → redirect dengan code
  POST /token                                   → tukar code → JWT (HS256)

State design:
  - users        : disimpan di auth.db (persisten)
  - clients/codes: disimpan di memory  (restart = Claude auto re-register)

Catatan keamanan (sengaja disederhanakan):
  - PKCE param diterima tapi TIDAK diverifikasi. Untuk production tambahkan
    pengecekan code_verifier vs code_challenge di /token.
  - Tidak ada refresh token; access token TTL = 1 jam.
"""

import os
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Route

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


SECRET = os.environ["JWT_SECRET"]  # 32+ char random
BASE_URL = os.environ.get("AUTH_BASE_URL", "http://localhost:9000")
print(
    f"Auth Server running with BASE_URL={BASE_URL} and AUTH_DB={os.environ.get('AUTH_DB', 'auth.db')}"
)
AUTH_DB = os.environ.get("AUTH_DB", "auth.db")
TOKEN_TTL = 3600

CLIENTS: dict[str, dict] = {}  # client_id → {redirect_uris}
CODES: dict[str, dict] = {}  # code      → {username, db_path, redirect_uri, exp}


def _init_db() -> None:
    with sqlite3.connect(AUTH_DB) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                db_path       TEXT NOT NULL
            )
        """)


def _get_user(username: str) -> dict | None:
    with sqlite3.connect(AUTH_DB) as c:
        row = c.execute(
            "SELECT password_hash, db_path FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return {"password_hash": row[0], "db_path": row[1]} if row else None


async def metadata(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "issuer": BASE_URL,
            "authorization_endpoint": f"{BASE_URL}/authorize",
            "token_endpoint": f"{BASE_URL}/token",
            "registration_endpoint": f"{BASE_URL}/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"],
        }
    )


async def register(request: Request) -> JSONResponse:
    body = await request.json()
    client_id = secrets.token_urlsafe(16)
    CLIENTS[client_id] = {"redirect_uris": body.get("redirect_uris", [])}
    return JSONResponse({"client_id": client_id, **CLIENTS[client_id]})


async def authorize(request: Request) -> HTMLResponse:
    p = request.query_params
    return HTMLResponse(f"""
      <form method="post" action="/login"
            style="font-family:sans-serif;max-width:300px;margin:5em auto">
        <h3>Login</h3>
        <input name="username" placeholder="username" autofocus
               style="display:block;width:100%;margin-bottom:.5em">
        <input name="password" type="password" placeholder="password"
               style="display:block;width:100%;margin-bottom:.5em">
        <input type="hidden" name="client_id"      value="{p.get("client_id", "")}">
        <input type="hidden" name="redirect_uri"   value="{p.get("redirect_uri", "")}">
        <input type="hidden" name="state"          value="{p.get("state", "")}">
        <input type="hidden" name="code_challenge" value="{p.get("code_challenge", "")}">
        <button style="width:100%">Login</button>
      </form>
    """)


async def login(request: Request):
    f = await request.form()
    user = _get_user(f["username"])
    if not user or not bcrypt.checkpw(
        f["password"].encode(), user["password_hash"].encode()
    ):
        return HTMLResponse("Login gagal", status_code=401)
    code = secrets.token_urlsafe(24)
    CODES[code] = {
        "username": f["username"],
        "db_path": user["db_path"],
        "redirect_uri": f["redirect_uri"],
        "exp": time.time() + 60,
    }
    return RedirectResponse(
        f"{f['redirect_uri']}?code={code}&state={f.get('state', '')}",
        status_code=302,
    )


async def token(request: Request) -> JSONResponse:
    f = await request.form()
    entry = CODES.pop(f["code"], None)
    if not entry or entry["exp"] < time.time():
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    now = int(time.time())
    access_token = jwt.encode(
        {
            "sub": entry["username"],
            "db_path": entry["db_path"],
            "iss": BASE_URL,
            "iat": now,
            "exp": now + TOKEN_TTL,
        },
        SECRET,
        algorithm="HS256",
    )
    return JSONResponse(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": TOKEN_TTL,
        }
    )


@asynccontextmanager
async def _lifespan(_app: Starlette):
    _init_db()
    yield


app = Starlette(
    lifespan=_lifespan,
    routes=[
        Route("/.well-known/oauth-authorization-server", metadata),
        Route("/register", register, methods=["POST"]),
        Route("/authorize", authorize),
        Route("/login", login, methods=["POST"]),
        Route("/token", token, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
