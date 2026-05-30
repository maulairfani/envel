"""
Internal routes — dipanggil service-to-service (mcp-server → auth-server),
bukan untuk client publik. Dilindungi shared secret (INTERNAL_API_KEY).
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from .. import repository, security
from ..config import settings

router = APIRouter(prefix="/internal")


class DbUrlRequest(BaseModel):
    username: str


class DbUrlResponse(BaseModel):
    db_url: str


def _check_internal(authorization: str | None = Header(default=None)) -> None:
    if authorization != f"Bearer {settings.internal_api_key}":
        raise HTTPException(status_code=401, detail="unauthorized")


@router.post("/db-url", response_model=DbUrlResponse)
def get_db_url(
    body: DbUrlRequest, _: None = Depends(_check_internal)
) -> DbUrlResponse:
    user = repository.get_user(body.username)
    if not user or not user.db_url_encrypted:
        raise HTTPException(status_code=404, detail="user_not_found_or_no_db_url")
    return DbUrlResponse(db_url=security.decrypt_url(user.db_url_encrypted))
