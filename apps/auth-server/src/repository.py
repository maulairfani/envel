from dataclasses import dataclass

import psycopg

from .config import settings


@dataclass
class User:
    username: str
    password_hash: str
    tier: str
    db_url_encrypted: bytes | None


def get_user(username: str) -> User | None:
    with psycopg.connect(settings.database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT username, password_hash, tier, db_url_encrypted FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
    return User(*row) if row else None


def create_user(username: str, password_hash: str, tier: str = "managed") -> None:
    """Insert the user without db_url_encrypted first — it is set later after provisioning."""
    with psycopg.connect(settings.database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, password_hash, tier) VALUES (%s, %s, %s)",
            (username, password_hash, tier),
        )
        conn.commit()


def set_db_url(username: str, db_url_encrypted: bytes) -> None:
    with psycopg.connect(settings.database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET db_url_encrypted = %s WHERE username = %s",
            (db_url_encrypted, username),
        )
        conn.commit()
