from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    auth_base_url: str = "http://localhost:9000"
    database_url: str
    token_ttl: int = 3600

    # Fernet key untuk encrypt db_url di kolom users.db_url_encrypted
    auth_data_key: str

    # MCP internal API
    mcp_internal_url: str  # e.g. http://mcp-server:8000
    internal_api_key: str  # shared secret antara auth ↔ mcp


settings = Settings()
