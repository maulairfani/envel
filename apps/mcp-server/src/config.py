from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    auth_base_url: str
    mcp_base_url: str
    managed_database_url: str
    internal_api_key: str  # shared secret untuk endpoint /internal/*


settings = Settings()
