"""
Schema provisioning untuk user managed.

Endpoint /internal/provision dipanggil oleh auth-server saat sign up:
  1. CREATE SCHEMA "user_<username>" di Postgres envel_managed
  2. Run alembic upgrade head untuk schema itu (via subprocess)
  3. Return URL: postgresql://...?options=-csearch_path=user_<username>
"""

import re
import subprocess
from pathlib import Path

import psycopg

from .config import settings

REPO_ROOT = Path(__file__).resolve().parents[1]
SAFE_USERNAME = re.compile(r"^[a-zA-Z0-9_]{1,64}$")


def _schema_name(username: str) -> str:
    if not SAFE_USERNAME.match(username):
        raise ValueError(f"invalid username: {username}")
    return f"user_{username}"


def _build_db_url(schema: str) -> str:
    # postgresql://user:pass@host:5432/db?options=-csearch_path=schema_name
    sep = "&" if "?" in settings.managed_database_url else "?"
    return f"{settings.managed_database_url}{sep}options=-csearch_path%3D{schema}"


def provision(username: str) -> str:
    schema = _schema_name(username)

    # 1. CREATE SCHEMA (idempoten — IF NOT EXISTS)
    with psycopg.connect(settings.managed_database_url) as conn, conn.cursor() as cur:
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        conn.commit()

    # 2. Run alembic upgrade untuk schema itu
    result = subprocess.run(
        ["alembic", "-x", f"schema={schema}", "upgrade", "head"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"alembic upgrade failed: {result.stderr or result.stdout}"
        )

    return _build_db_url(schema)
