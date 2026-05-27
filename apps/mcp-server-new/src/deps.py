"""
Request-scoped helpers untuk tools.

- current_user(): baca JWT (verified by FastMCP), fetch db_url dari auth via
  /internal/db-url (cache 5 menit per username).
- user_session(db_url): yield SQLAlchemy session ke schema user. Engine
  di-cache per db_url (tidak di-dispose) supaya tidak buka TCP+auth per request.
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass

import httpx
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .config import settings


@dataclass
class CurrentUser:
    username: str
    db_url: str


# ─── Caches ───
_engines: dict[str, Engine] = {}
_url_cache: dict[str, tuple[str, float]] = {}  # username → (db_url, expires_at)
_URL_CACHE_TTL = 300  # 5 menit


def _fetch_db_url(username: str) -> str:
    now = time.time()
    cached = _url_cache.get(username)
    if cached and cached[1] > now:
        return cached[0]

    resp = httpx.post(
        f"{settings.auth_base_url.rstrip('/')}/internal/db-url",
        json={"username": username},
        headers={"Authorization": f"Bearer {settings.internal_api_key}"},
        timeout=10.0,
    )
    resp.raise_for_status()
    url = resp.json()["db_url"]
    _url_cache[username] = (url, now + _URL_CACHE_TTL)
    return url


def current_user() -> CurrentUser:
    token = get_access_token()
    username = token.claims["sub"]
    db_url = _fetch_db_url(username)
    return CurrentUser(username=username, db_url=db_url)


def _get_engine(db_url: str) -> Engine:
    if db_url not in _engines:
        _engines[db_url] = create_engine(db_url, future=True, pool_pre_ping=True)
    return _engines[db_url]


@contextmanager
def user_session(db_url: str):
    engine = _get_engine(db_url)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as session:
        yield session
