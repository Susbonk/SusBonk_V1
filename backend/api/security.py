from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

from settings import settings
from logger import get_logger


log = get_logger(__name__)

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    log.debug("Hashing password")
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    log.debug("Verifying password")
    return pwd_context.verify(password, password_hash)


def create_access_token(*, sub: UUID, ttl_minutes: int) -> str:
    log.debug(f"Creating access token for user: {sub}, TTL: {ttl_minutes} minutes")
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(sub),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    log.info(f"Successfully created access token for user: {sub}")
    return token


def decode_token(token: str) -> dict[str, Any]:
    log.debug("Decoding JWT token")
    try:
        decoded_payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        log.info("Successfully decoded JWT token")
        return decoded_payload
    except jwt.ExpiredSignatureError:
        log.info("JWT token has expired")
        raise
    except jwt.InvalidTokenError:
        log.warning("Invalid JWT token")
        raise
