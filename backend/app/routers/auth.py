from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
import jwt

from app.core.config import settings
from app.core.deps import CurrentUserDep, SessionDep, BearerCredentialsDep
from app.models.database import User
from app.services.auth_tokens import (
    blacklist_token,
    create_access_token,
    decode_access_token,
    generate_nonce,
    store_nonce,
    verify_nonce,
    clear_nonce,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class VerifyRequest(BaseModel):
    wallet_address: str = Field(min_length=32, max_length=44)
    signature: str
    nonce: str


@router.get("/nonce")
async def get_nonce(wallet_address: str) -> dict[str, Any]:
    nonce = generate_nonce()
    await store_nonce(
        wallet_address=wallet_address,
        nonce=nonce,
        ttl_seconds=max(60, settings.NONCE_EXPIRE_MINUTES * 60),
    )
    return {"nonce": nonce}


@router.post("/verify")
async def verify_wallet(payload: VerifyRequest, session: SessionDep) -> dict[str, Any]:
    # 1. Verify the nonce
    if not await verify_nonce(payload.wallet_address, payload.nonce):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired nonce",
        )

    # 2. Verify the Ed25519 signature
    try:
        pubkey_bytes = base58.b58decode(payload.wallet_address)
        verify_key = VerifyKey(pubkey_bytes)
        # The message format follows standard Solana SIWS (or plain message)
        message = f"Sign this message to authenticate with ASE. Nonce: {payload.nonce}".encode("utf-8")
        signature_bytes = base58.b58decode(payload.signature)
        verify_key.verify(message, signature_bytes)
    except (ValueError, BadSignatureError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # 3. Mark nonce as used
    await clear_nonce(payload.wallet_address)

    # 4. Find or create user
    try:
        result = await session.execute(
            select(User).filter(User.wallet_address == payload.wallet_address)
        )
        user = result.scalars().first()
        
        if not user:
            user = User(wallet_address=payload.wallet_address)
            session.add(user)
            await session.commit()
    except (DBAPIError, SQLAlchemyError):
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable",
        )

    # 5. Issue JWT
    user_id = str(user.id)
    token, expires_at = create_access_token(user_id, payload.wallet_address)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user_id,
            "wallet_address": payload.wallet_address,
        },
    }


@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> dict[str, Any]:
    return {
        "id": str(current_user.id),
        "wallet_address": current_user.wallet_address,
    }


@router.post("/logout")
async def logout(
    current_user: CurrentUserDep,
    credentials: BearerCredentialsDep,
) -> dict[str, str]:
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

    jti = payload.get("jti")
    exp = payload.get("exp")
    sub = payload.get("sub")
    if not jti or not exp or not sub or str(current_user.id) != str(sub):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    if isinstance(exp, datetime):
        expires_unix = int(exp.replace(tzinfo=timezone.utc).timestamp())
    else:
        expires_unix = int(exp)

    await blacklist_token(jti, expires_unix)
    return {"message": "Logged out"}
