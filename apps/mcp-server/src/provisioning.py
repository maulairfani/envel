"""
Schema provisioning for managed users.

The /internal/provision endpoint is called by auth-server on sign up:
  1. CREATE ROLE per user (random password, LOGIN, no superuser)
  2. CREATE SCHEMA, owner = admin (not the user) → the user has no CREATE
  3. GRANT SELECT/INSERT/UPDATE/DELETE on tables + default privileges
  4. Run alembic upgrade head (using the admin URL, since DDL is needed)
  5. Return a URL with the user role's credentials (not admin)

The user role does NOT have:
  - CREATE / DROP / ALTER (DDL)
  - Access to other schemas
  - Superuser flag

So query tools (that use this role) can only SELECT/INSERT/UPDATE/DELETE
in their own schema. DDL is rejected by Postgres.
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
    """Create role + schema + grants. Use psycopg.sql.Identifier for safe escaping."""
    ident_schema = sql.Identifier(schema)
    ident_role = sql.Identifier(role)

    with conn.cursor() as cur:
        # 1. CREATE ROLE (LOGIN, password). DDL does not accept parameter binding,
        # so use sql.Literal which escapes the string safely.
        cur.execute(
            sql.SQL("CREATE ROLE {role} WITH LOGIN PASSWORD {pw}").format(
                role=ident_role, pw=sql.Literal(password)
            )
        )

        # 2. CREATE SCHEMA — owner = current_user (admin), not user_role
        cur.execute(sql.SQL("CREATE SCHEMA {schema}").format(schema=ident_schema))

        # 3. USAGE on the schema (so the user can "see" the schema)
        cur.execute(
            sql.SQL("GRANT USAGE ON SCHEMA {schema} TO {role}").format(
                schema=ident_schema, role=ident_role
            )
        )

        # 4. DML grant on all existing tables (empty at first, but safe)
        cur.execute(
            sql.SQL(
                "GRANT SELECT, INSERT, UPDATE, DELETE "
                "ON ALL TABLES IN SCHEMA {schema} TO {role}"
            ).format(schema=ident_schema, role=ident_role)
        )

        # 5. DEFAULT PRIVILEGES: when admin (envel) creates new tables in this schema
        #    (via alembic upgrade), automatically grant them to user_role.
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} "
                "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role}"
            ).format(schema=ident_schema, role=ident_role)
        )

        # 6. Forward-compat for sequences (in case models later use SERIAL/sequences)
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

    # 1-2-3. Setup role + schema + grants (as admin)
    with psycopg.connect(settings.managed_database_url) as conn:
        _setup_role_and_schema(conn, schema, role, password)
        conn.commit()

    # 4. Run alembic upgrade — use admin URL (settings.managed_database_url)
    #    since CREATE TABLE privilege is needed. Created tables automatically get
    #    grants via the ALTER DEFAULT PRIVILEGES above.
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

    # 5. Build URL with the user role (limited privileges)
    return _build_user_url(role, password, schema)
