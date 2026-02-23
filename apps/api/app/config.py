"""Application configuration loaded from environment variables."""

import logging
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://localhost/financialanalyst"

    # JWT
    secret_key: str = "changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Plaid
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"

    # OpenAI
    openai_api_key: str = ""

    # Fernet key for Plaid access tokens at rest
    encryption_key: str = ""

    # CORS — comma-separated list
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.secret_key == "changeme" and os.environ.get("APP_ENV", "development") == "production":
        raise RuntimeError("SECRET_KEY must be set to a secure value in production")
    if s.secret_key == "changeme":
        logger.warning("SECRET_KEY is using insecure default 'changeme' — set a real value in .env")
    return s


settings: Settings = get_settings()

