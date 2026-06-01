import psycopg
from fastapi import APIRouter, HTTPException

from .. import provisioning, repository, security
from ..schemas import SignupRequest, SignupResponse

router = APIRouter()


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(body: SignupRequest) -> SignupResponse:
    # 1. Hash password & insert user (without db_url)
    pw_hash = security.hash_password(body.password)
    try:
        repository.create_user(body.username, pw_hash, tier="managed")
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="username_taken")

    # 2. Call MCP to create the schema + run alembic migrate, get db_url
    try:
        db_url = await provisioning.provision_managed_user(body.username)
    except provisioning.ProvisioningError as e:
        # User row was already created but provisioning failed — leave it, can be retried manually.
        # TODO: queue retry / rollback user row
        raise HTTPException(status_code=502, detail=f"provisioning_failed: {e}")

    # 3. Encrypt + save
    repository.set_db_url(body.username, security.encrypt_url(db_url))

    return SignupResponse(username=body.username, tier="managed")
