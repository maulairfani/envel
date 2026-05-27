from fastapi import APIRouter, Form, HTTPException

from .. import services
from ..schemas import ClientRegisterRequest, ClientRegisterResponse, TokenResponse

router = APIRouter()


@router.post("/register", response_model=ClientRegisterResponse)
def register(body: ClientRegisterRequest) -> ClientRegisterResponse:
    client_id, redirect_uris = services.register_client(body.redirect_uris)
    return ClientRegisterResponse(client_id=client_id, redirect_uris=redirect_uris)


@router.post("/token", response_model=TokenResponse)
def token(code: str = Form(...)) -> TokenResponse:
    result = services.exchange_token(code)
    if result is None:
        raise HTTPException(status_code=400, detail="invalid_grant")
    return result
