from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl

from .config import settings

_verifier = JWTVerifier(public_key=settings.jwt_secret, algorithm="HS256")

auth = RemoteAuthProvider(
    token_verifier=_verifier,
    authorization_servers=[AnyHttpUrl(settings.auth_public_url)],
    base_url=AnyHttpUrl(settings.mcp_base_url),
)
