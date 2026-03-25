from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets
from typing import Any

import jwt
from redis.asyncio import Redis

from app.core.config import settings


_redis_client: Redis | None = None
_otp_fallback_store: dict[str, tuple[str, int]] = {}
_blacklist_fallback_store: dict[str, int] = {}
logger = logging.getLogger(__name__)


def _unix_now() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _purge_expired_fallbacks() -> None:
    now = _unix_now()
    for key, (_, expires_at) in list(_otp_fallback_store.items()):
        if expires_at <= now:
            _otp_fallback_store.pop(key, None)
    for key, expires_at in list(_blacklist_fallback_store.items()):
        if expires_at <= now:
            _blacklist_fallback_store.pop(key, None)


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
    key = _otp_key(email)
    value = _hash_otp(email, otp_code)
    try:
        redis = get_redis_client()
        await redis.setex(key, ttl_seconds, value)
        return
    except Exception:
        logger.warning("Redis unavailable while storing OTP; using in-memory fallback")

    _purge_expired_fallbacks()
    _otp_fallback_store[key] = (value, _unix_now() + ttl_seconds)


async def verify_stored_otp(email: str, otp_code: str) -> bool:
    key = _otp_key(email)
    stored = None

    try:
        redis = get_redis_client()
        stored = await redis.get(key)
    except Exception:
        logger.warning(
            "Redis unavailable while verifying OTP; using in-memory fallback"
        )

    if stored is None:
        _purge_expired_fallbacks()
        fallback = _otp_fallback_store.get(key)
        stored = fallback[0] if fallback else None

    if not stored:
        return False

    candidate = _hash_otp(email, otp_code)
    return hmac.compare_digest(stored, candidate)


async def clear_verification_otp(email: str) -> None:
    key = _otp_key(email)
    try:
        redis = get_redis_client()
        await redis.delete(key)
    except Exception:
        logger.warning("Redis unavailable while clearing OTP; using in-memory fallback")

    _otp_fallback_store.pop(key, None)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


async def blacklist_token(jti: str, expires_at_unix: int) -> None:
    now = _unix_now()
    ttl_seconds = max(1, expires_at_unix - now)
    key = f"jwt:blacklist:{jti}"
    try:
        redis = get_redis_client()
        await redis.setex(key, ttl_seconds, "1")
        return
    except Exception:
        logger.warning(
            "Redis unavailable while blacklisting JWT; using in-memory fallback"
        )

    _purge_expired_fallbacks()
    _blacklist_fallback_store[key] = now + ttl_seconds


async def is_token_blacklisted(jti: str) -> bool:
    key = f"jwt:blacklist:{jti}"

    try:
        redis = get_redis_client()
        value = await redis.get(key)
        if value is not None:
            return True
    except Exception:
        logger.warning(
            "Redis unavailable while checking JWT blacklist; using in-memory fallback"
        )

    _purge_expired_fallbacks()
    expires_at = _blacklist_fallback_store.get(key)
    return expires_at is not None and expires_at > _unix_now()
