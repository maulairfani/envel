"""
Schema provisioning untuk user managed.

Endpoint /internal/provision dipanggil oleh auth-server saat sign up:
  1. CREATE ROLE per user (random password, LOGIN, no superuser)
  2. CREATE SCHEMA, owner = admin (bukan user) → user tidak punya CREATE
  3. GRANT SELECT/INSERT/UPDATE/DELETE pada tables + default privileges
  4. Run alembic upgrade head (pakai admin URL, karena butuh DDL)
  5. Return URL ber-credential role user (bukan admin)

Role user TIDAK punya:
  - CREATE / DROP / ALTER (DDL)
  - Access ke schema lain
  - Superuser flag

Jadi tool query (yang pakai role ini) cuma bisa SELECT/INSERT/UPDATE/DELETE
di schema sendiri. DDL ditolak Postgres.
"""

import re
import secrets
import subprocess
from pathlib import Path
from urllib.parse import quote, urlparse

import psycopg
from psycopg import sql

from .config import settings

REPO_ROOT = Path(__file__).resolve().parents[1]
SAFE_USERNAME = re.compile(r"^[a-zA-Z0-9_]{1,64}$")


def _schema_name(username: str) -> str:
    if not SAFE_USERNAME.match(username):
        raise ValueError(f"invalid username: {username}")
    return f"user_{username}"


def _build_user_url(role: str, password: str, schema: str) -> str:
    admin = urlparse(settings.managed_database_url)
    return (
        f"postgresql://{role}:{quote(password)}"
        f"@{admin.hostname}:{admin.port or 5432}{admin.path}"
        f"?options=-csearch_path%3D{schema}"
    )


def _setup_role_and_schema(conn: psycopg.Connection, schema: str, role: str, password: str) -> None:
    """Create role + schema + grants. Pakai psycopg.sql.Identifier untuk escape aman."""
    ident_schema = sql.Identifier(schema)
    ident_role = sql.Identifier(role)

    with conn.cursor() as cur:
        # 1. CREATE ROLE (LOGIN, password). DDL tidak terima parameter binding,
        # jadi pakai sql.Literal yang escape string secara aman.
        cur.execute(
            sql.SQL("CREATE ROLE {role} WITH LOGIN PASSWORD {pw}").format(
                role=ident_role, pw=sql.Literal(password)
            )
        )

        # 2. CREATE SCHEMA — owner = current_user (admin), bukan user_role
        cur.execute(sql.SQL("CREATE SCHEMA {schema}").format(schema=ident_schema))

        # 3. USAGE pada schema (user bisa "lihat" schema)
        cur.execute(
            sql.SQL("GRANT USAGE ON SCHEMA {schema} TO {role}").format(
                schema=ident_schema, role=ident_role
            )
        )

        # 4. DML grant pada semua tabel existing (kosong saat awal, tapi safe)
        cur.execute(
            sql.SQL(
                "GRANT SELECT, INSERT, UPDATE, DELETE "
                "ON ALL TABLES IN SCHEMA {schema} TO {role}"
            ).format(schema=ident_schema, role=ident_role)
        )

        # 5. DEFAULT PRIVILEGES: saat admin (envel) create tabel baru di schema ini
        #    (lewat alembic upgrade), grant otomatis ke user_role.
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
                "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role}"
            ).format(schema=ident_schema, role=ident_role)
        )

        # 6. Forward-compat untuk sequence (jika model nantinya pakai SERIAL/sequence)
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
                "GRANT USAGE, SELECT ON SEQUENCES TO {role}"
            ).format(schema=ident_schema, role=ident_role)
        )


def provision(username: str) -> str:
    schema = _schema_name(username)
    role = schema  # role name = schema name (1:1 mapping)
    password = secrets.token_urlsafe(32)

    # 1-2-3. Setup role + schema + grants (sebagai admin)
    with psycopg.connect(settings.managed_database_url) as conn:
        _setup_role_and_schema(conn, schema, role, password)
        conn.commit()

    # 4. Run alembic upgrade — pakai admin URL (settings.managed_database_url)
    #    karena butuh CREATE TABLE privilege. Tabel yang dibuat otomatis dapat
    #    grant via ALTER DEFAULT PRIVILEGES di atas.
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

    # 5. Build URL dengan role user (limited privileges)
    return _build_user_url(role, password, schema)
