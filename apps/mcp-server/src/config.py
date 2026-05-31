from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    auth_base_url: str  # INTERNAL — for /internal/db-url calls (e.g. http://auth-server:9000)
    auth_public_url: str = "http://localhost:9000"  # PUBLIC — advertised in OAuth metadata to external MCP clients
    mcp_base_url: str
    internal_api_key: str  # shared secret untuk endpoint /internal/*

    # Managed Postgres — the connection URL is derived from these parts, so the
    # full URL is never an env var nor injected by docker-compose.
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres-managed"
    postgres_port: int = 5432

    @property
    def managed_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
