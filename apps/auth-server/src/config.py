from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    auth_base_url: str = "http://localhost:9000"
    token_ttl: int = 3600

    # Fernet key to encrypt db_url in the users.db_url_encrypted column
    auth_data_key: str

    # MCP internal API
    mcp_internal_url: str  # e.g. http://mcp-server:8000
    internal_api_key: str  # shared secret between auth ↔ mcp

    # Auth Postgres — URL derived from these parts (no full-URL env var).
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres-auth"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
