from typing import Annotated, AsyncGenerator
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.vectorizer import Vectorizer
from app.services.auth_tokens import decode_access_token, is_token_blacklisted


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


class TokenUser(BaseModel):
    id: str
    wallet_address: str


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> TokenUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    sub = payload.get("sub")
    wallet_address = payload.get("wallet_address")
    jti = payload.get("jti")
    if not sub or not wallet_address or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    if await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    return TokenUser(id=str(user_id), wallet_address=wallet_address)


CurrentUserDep = Annotated[TokenUser, Depends(get_current_user)]


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> TokenUser | None:
    if not credentials:
        return None

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        return None

    sub = payload.get("sub")
    wallet_address = payload.get("wallet_address")
    jti = payload.get("jti")
    if not sub or not wallet_address or not jti:
        return None

    if await is_token_blacklisted(jti):
        return None

    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError):
        return None

    return TokenUser(id=str(user_id), wallet_address=wallet_address)


OptionalUserDep = Annotated[TokenUser | None, Depends(get_optional_user)]
BearerCredentialsDep = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]
