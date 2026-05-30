import time

import bcrypt
import jwt
from cryptography.fernet import Fernet

from .config import settings

_fernet = Fernet(settings.auth_data_key.encode())


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def encrypt_url(plaintext: str) -> bytes:
    return _fernet.encrypt(plaintext.encode())


def decrypt_url(ciphertext: bytes) -> str:
    return _fernet.decrypt(ciphertext).decode()


def create_access_token(username: str) -> tuple[str, int]:
    now = int(time.time())
    payload = {
        "sub": username,
        "iss": settings.auth_base_url,
        "iat": now,
        "exp": now + settings.token_ttl,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, settings.token_ttl
