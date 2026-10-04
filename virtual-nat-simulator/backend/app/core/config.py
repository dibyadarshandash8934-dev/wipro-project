from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Virtual NAT Gateway Simulator"
    debug: bool = False
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
