from fastapi import APIRouter

from ..config import settings
from ..schemas import OAuthMetadata

router = APIRouter()


@router.get(
    "/.well-known/oauth-authorization-server",
    response_model=OAuthMetadata,
)
def oauth_metadata() -> OAuthMetadata:
    base = settings.auth_base_url
    return OAuthMetadata(
        issuer=base,
        authorization_endpoint=f"{base}/authorize",
        token_endpoint=f"{base}/token",
        registration_endpoint=f"{base}/register",
        response_types_supported=["code"],
        grant_types_supported=["authorization_code"],
        code_challenge_methods_supported=["S256"],
    )
