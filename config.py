import os
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///dev.db")

    @property
    def db_type(self):
        return "postgres" if "postgresql" in self.DATABASE_URL else "sqlite"

# Load the configuration
settings = Config()