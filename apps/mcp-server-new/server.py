from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.lifespan import lifespan
from pydantic import AnyHttpUrl
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from master_db import init_master_db
from user_db import init_user_db

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MASTER_DB_PATH = DATA_DIR / "master.db"

master_engine: Engine | None = None
MasterSession: sessionmaker[Session] | None = None


@contextmanager
def _user_session(db_path: Path):
    user_engine, UserSession = init_user_db(db_path)
    try:
        with UserSession() as session:
            yield session
    finally:
        user_engine.dispose()


@lifespan
async def app_lifespan(_: FastMCP):
    global master_engine, MasterSession

    master_engine, MasterSession = init_master_db(DATA_DIR, MASTER_DB_PATH)

    yield {}

    if master_engine is not None:
        master_engine.dispose()
        master_engine = None
        MasterSession = None


verifier = JWTVerifier(public_key=os.environ["JWT_SECRET"], algorithm="HS256")
auth = RemoteAuthProvider(
    token_verifier=verifier,
    authorization_servers=[AnyHttpUrl(os.environ["AUTH_BASE_URL"])],
    base_url=AnyHttpUrl(os.environ["MCP_BASE_URL"]),
)
mcp = FastMCP("DataAnalysis", lifespan=app_lifespan, auth=auth)


@mcp.tool
def query_tool(query: str) -> dict[str, Any]:
    sql = query.strip()
    if not sql:
        raise ValueError("query cannot be empty")

    token = get_access_token()
    username = token.claims["sub"]
    db_path = Path(token.claims["db_path"])

    with _user_session(db_path) as session:
        result = session.execute(text(sql))

        if result.returns_rows:
            rows = [dict(row._mapping) for row in result.fetchall()]
            return {
                "ok": True,
                "username": username,
                "db_path": str(db_path),
                "rows": rows,
                "rowcount": len(rows),
            }

        session.commit()
        return {
            "ok": True,
            "username": username,
            "db_path": str(db_path),
            "rows": [],
            "rowcount": result.rowcount,
        }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
