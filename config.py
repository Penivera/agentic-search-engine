import os
from pydantic import BaseSettings

class Config(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/agentic")

# Load the configuration
settings = Config()