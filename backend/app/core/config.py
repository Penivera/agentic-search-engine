import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Allow extra keys in .env without crashing
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = Field(default="sqlite:///dev.db")
    INGEST_API_TOKENS: str = Field(default="")
    SEARCH_CACHE_TTL_SECONDS: int = Field(default=60)
    JWT_SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    OTP_EXPIRE_MINUTES: int = Field(default=10)
    OTP_DEBUG_EXPOSE_CODE: bool = Field(default=True)
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_SEND_FROM_MAIL: str = Field(default="")
    SMTP_USE_STARTTLS: bool = Field(default=True)
    SMTP_TIMEOUT_SECONDS: int = Field(default=20)

    @property
    def db_type(self):
        return "postgres" if "postgresql" in self.DATABASE_URL else "sqlite"

    @property
    def ingest_tokens(self) -> set[str]:
        if not self.INGEST_API_TOKENS:
            return set()
        return {
            token.strip()
            for token in self.INGEST_API_TOKENS.split(",")
            if token.strip()
        }


# Load the configuration
settings = Settings()
