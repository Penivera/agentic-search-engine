import os
from pydantic_settings import BaseSettings
from pydantic import Field, SettingsConfigDict

class Settings(BaseSettings):
    # Allow extra keys in .env without crashing
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_URL: str = Field(..., description="Database connection URL")
    DATABASE_URL: str = Field(default="sqlite:///dev.db", env="DATABASE_URL")

    @property
    def db_type(self):
        return "postgres" if "postgresql" in self.DATABASE_URL else "sqlite"

# Load the configuration
settings = Config()