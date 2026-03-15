from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import init_db
from app.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield

# Initialize the application
app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root() -> dict[str, str]:
    return {"message": "API running with integrated FastAPI skill"}

# Register API routes
app.include_router(api_router)