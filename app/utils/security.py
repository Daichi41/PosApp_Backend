from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"


class TokenError(Exception):
    """Raised when JWT validation fails."""


def hash_password(password: str) -> str:
    """Generate a deterministic SHA-256 hash for the given password."""

    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Compare a raw password against a stored hash in constant time."""

    candidate = hash_password(password)
    return hmac.compare_digest(candidate, password_hash)


def create_access_token(user_id: int, expires_minutes: int | None = None) -> str:
    """Build a signed JWT for the provided user identifier."""

    settings = get_settings()
    expires_in = expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    if expires_in <= 0:
        expires_in = settings.access_token_expire_minutes

    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=expires_in)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }

    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Decode and validate an incoming JWT returning its payload."""

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:  # pragma: no cover - exercised via tests
        raise TokenError("Invalid token") from exc

    if "sub" not in payload:
        raise TokenError("Token missing subject")

    return payload
