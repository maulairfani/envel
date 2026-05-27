import secrets
import time

from . import repository, security, stores
from .schemas import TokenResponse


CODE_TTL = 60


def register_client(redirect_uris: list[str]) -> tuple[str, list[str]]:
    client_id = secrets.token_urlsafe(16)
    stores.clients[client_id] = {"redirect_uris": redirect_uris}
    return client_id, redirect_uris


def issue_code(username: str, password: str, redirect_uri: str) -> str | None:
    user = repository.get_user(username)
    if not user or not security.verify_password(password, user.password_hash):
        return None
    code = secrets.token_urlsafe(24)
    stores.codes[code] = {
        "username": user.username,
        "redirect_uri": redirect_uri,
        "exp": time.time() + CODE_TTL,
    }
    return code


def exchange_token(code: str) -> TokenResponse | None:
    entry = stores.codes.pop(code, None)
    if not entry or entry["exp"] < time.time():
        return None
    token, ttl = security.create_access_token(entry["username"])
    return TokenResponse(access_token=token, expires_in=ttl)
