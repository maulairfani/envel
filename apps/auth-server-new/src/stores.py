"""
Ephemeral in-memory stores.

Restart-safe by design: OAuth clients auto re-register, codes punya TTL 60 detik.
"""

clients: dict[str, dict] = {}  # client_id → {redirect_uris}
codes: dict[str, dict] = {}    # code → {username, db_path, redirect_uri, exp}
