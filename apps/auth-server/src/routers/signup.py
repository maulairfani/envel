import psycopg
from fastapi import APIRouter, HTTPException

from .. import provisioning, repository, security
from ..schemas import SignupRequest, SignupResponse

router = APIRouter()


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(body: SignupRequest) -> SignupResponse:
    # 1. Hash password & insert user (tanpa db_url)
    pw_hash = security.hash_password(body.password)
    try:
        repository.create_user(body.username, pw_hash, tier="managed")
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="username_taken")

    # 2. Call MCP untuk bikin schema + alembic migrate, dapat db_url
    try:
        db_url = await provisioning.provision_managed_user(body.username)
    except provisioning.ProvisioningError as e:
        # User row sudah dibuat tapi provisioning gagal — biarkan, bisa di-retry manual.
        # TODO: queue retry / rollback user row
        raise HTTPException(status_code=502, detail=f"provisioning_failed: {e}")

    # 3. Encrypt + simpan
    repository.set_db_url(body.username, security.encrypt_url(db_url))

    return SignupResponse(username=body.username, tier="managed")
