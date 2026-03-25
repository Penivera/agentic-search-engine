from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import secrets
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
import jwt

from app.core.config import settings
from app.core.deps import CurrentUserDep, SessionDep, BearerCredentialsDep
from app.models.database import User
from app.services.auth_tokens import (
    blacklist_token,
    clear_verification_otp,
    create_access_token,
    decode_access_token,
    generate_otp_code,
    store_verification_otp,
    verify_stored_otp,
)
from app.services.mailer import EmailDeliveryError, send_verification_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=4, max_length=10)


class ResendOtpRequest(BaseModel):
    email: EmailStr


def _otp_response_base(email: str, otp_code: str) -> dict[str, Any]:
    data: dict[str, Any] = {
        "message": "Verification code sent",
        "verification_required": True,
        "email": email.lower(),
        "otp_expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60,
    }
    if settings.OTP_DEBUG_EXPOSE_CODE:
        data["dev_otp"] = otp_code
    return data


async def _issue_and_store_otp(email: str) -> str:
    otp_code = generate_otp_code()
    await store_verification_otp(
        email=email,
        otp_code=otp_code,
        ttl_seconds=max(60, settings.OTP_EXPIRE_MINUTES * 60),
    )

    try:
        await send_verification_otp_email(email, otp_code)
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to deliver OTP email: {exc}",
        )

    return otp_code


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000
    )
    return digest.hex()


def _build_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = _hash_password(password, salt)
    return f"{salt}:{digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split(":", 1)
    except ValueError:
        return False

    expected = _hash_password(password, salt)
    return secrets.compare_digest(expected, digest)


@router.post("/register")
async def register_user(
    payload: RegisterRequest, session: SessionDep
) -> dict[str, Any]:
    normalized_email = payload.email.lower()
    existing = await session.execute(
        select(User).filter(User.email == normalized_email)
    )
    user = existing.scalars().first()

    if user and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    if user:
        # Allow re-register for unverified accounts and rotate password hash.
        user.password_hash = _build_password_hash(payload.password)
        user.is_verified = False
        user.verified_at = None
    else:
        user = User(
            email=normalized_email,
            password_hash=_build_password_hash(payload.password),
            is_verified=False,
            verified_at=None,
        )
        session.add(user)

    await session.commit()
    otp_code = await _issue_and_store_otp(normalized_email)

    return _otp_response_base(normalized_email, otp_code)


@router.post("/verify-otp")
async def verify_otp(payload: VerifyOtpRequest, session: SessionDep) -> dict[str, Any]:
    normalized_email = payload.email.lower()
    result = await session.execute(select(User).filter(User.email == normalized_email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not await verify_stored_otp(normalized_email, payload.otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP code",
        )

    user_id = str(user.id)
    user_email = user.email
    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    await clear_verification_otp(normalized_email)

    token, expires_at = create_access_token(user_id, user_email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user_id,
            "email": user_email,
        },
    }


@router.post("/resend-otp")
async def resend_otp(payload: ResendOtpRequest, session: SessionDep) -> dict[str, Any]:
    normalized_email = payload.email.lower()
    result = await session.execute(select(User).filter(User.email == normalized_email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already verified",
        )

    otp_code = await _issue_and_store_otp(normalized_email)
    return _otp_response_base(normalized_email, otp_code)


@router.post("/login")
async def login_user(payload: LoginRequest, session: SessionDep) -> dict[str, Any]:
    result = await session.execute(
        select(User).filter(User.email == payload.email.lower())
    )
    user = result.scalars().first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Verify OTP first.",
        )

    token, expires_at = create_access_token(str(user.id), user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
        },
    }


@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> dict[str, Any]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
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
