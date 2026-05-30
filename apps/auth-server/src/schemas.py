from pydantic import BaseModel


class ClientRegisterRequest(BaseModel):
    redirect_uris: list[str] = []


class ClientRegisterResponse(BaseModel):
    client_id: str
    redirect_uris: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class SignupRequest(BaseModel):
    username: str
    password: str


class SignupResponse(BaseModel):
    username: str
    tier: str


class OAuthMetadata(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: str
    response_types_supported: list[str]
    grant_types_supported: list[str]
    code_challenge_methods_supported: list[str]
