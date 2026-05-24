"""
Admin CLI untuk tambah user.

Usage:
  python add_user.py <username> <password> [db_path]

Contoh:
  python add_user.py alice supersecret
  python add_user.py bob secret123 /data/bob.db

db_path default: ./data/user_<username>.db
"""
import sys
import sqlite3
from pathlib import Path

import bcrypt


AUTH_DB = Path(__file__).parent / "auth.db"


def main() -> None:
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) == 4 else str(
        Path(__file__).parent / "data" / f"user_{username}.db"
    )
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with sqlite3.connect(AUTH_DB) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                db_path       TEXT NOT NULL
            )
        """)
        try:
            c.execute(
                "INSERT INTO users (username, password_hash, db_path) VALUES (?, ?, ?)",
                (username, hashed, db_path),
            )
        except sqlite3.IntegrityError:
            print(f"User '{username}' sudah ada.")
            sys.exit(1)

    print(f"User '{username}' ditambahkan → {db_path}")


if __name__ == "__main__":
    main()
