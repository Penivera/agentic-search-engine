from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.services.vectorizer import Vectorizer

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db

# We cache Vectorizer so we don't reload the SentenceTransformer model on every request
_vectorizer_instance = Vectorizer()

def get_vectorizer() -> Vectorizer:
    return _vectorizer_instance

SessionDep = Annotated[AsyncSession, Depends(get_db)]
VectorizerDep = Annotated[Vectorizer, Depends(get_vectorizer)]
