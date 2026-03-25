from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from typing import Any

import jwt
from redis.asyncio import Redis

from app.core.config import settings


_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def _otp_key(email: str) -> str:
    return f"otp:verify:{email.lower()}"


def _hash_otp(email: str, otp_code: str) -> str:
    # Bind OTP hash to email and secret to prevent cross-account replay.
    raw = f"{email.lower()}:{otp_code}".encode("utf-8")
    secret = settings.JWT_SECRET_KEY.encode("utf-8")
    return hmac.new(secret, raw, hashlib.sha256).hexdigest()


def create_access_token(user_id: str, email: str) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    jti = secrets.token_urlsafe(18)

    payload = {
        "sub": user_id,
        "email": email,
        "jti": jti,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token, expires_at


def generate_otp_code(length: int = 6) -> str:
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


async def store_verification_otp(email: str, otp_code: str, ttl_seconds: int) -> None:
    redis = get_redis_client()
    await redis.setex(_otp_key(email), ttl_seconds, _hash_otp(email, otp_code))


async def verify_stored_otp(email: str, otp_code: str) -> bool:
    redis = get_redis_client()
    stored = await redis.get(_otp_key(email))
    if not stored:
        return False

    candidate = _hash_otp(email, otp_code)
    return hmac.compare_digest(stored, candidate)


async def clear_verification_otp(email: str) -> None:
    redis = get_redis_client()
    await redis.delete(_otp_key(email))


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


async def blacklist_token(jti: str, expires_at_unix: int) -> None:
    now = int(datetime.now(timezone.utc).timestamp())
    ttl_seconds = max(1, expires_at_unix - now)
    redis = get_redis_client()
    await redis.setex(f"jwt:blacklist:{jti}", ttl_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    redis = get_redis_client()
    value = await redis.get(f"jwt:blacklist:{jti}")
    return value is not None
