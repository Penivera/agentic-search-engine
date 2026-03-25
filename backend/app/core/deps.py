from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.services.vectorizer import Vectorizer
from app.core.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db


# We cache Vectorizer so we don't reload the SentenceTransformer model on every request
_vectorizer_instance: Vectorizer | None = None


def get_vectorizer() -> Vectorizer:
    global _vectorizer_instance
    if _vectorizer_instance is None:
        _vectorizer_instance = Vectorizer()
    return _vectorizer_instance


SessionDep = Annotated[AsyncSession, Depends(get_db)]
VectorizerDep = Annotated[Vectorizer, Depends(get_vectorizer)]

_bearer = HTTPBearer(auto_error=False)


def require_ingest_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> None:
    # If tokens are not configured, keep local development friction low.
    valid_tokens = settings.ingest_tokens
    if not valid_tokens:
        return

    if not credentials or credentials.credentials not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token",
        )


IngestAuthDep = Annotated[None, Depends(require_ingest_token)]
