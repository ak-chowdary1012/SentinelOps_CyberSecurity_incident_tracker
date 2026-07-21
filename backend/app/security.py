import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import get_settings


settings = get_settings()
ALGORITHM = "HS256"
MAX_BCRYPT_BYTES = 72


def validate_password_strength(password: str) -> None:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long")
    if len(password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("Password must be 72 bytes or fewer")
    checks = [
        (r"[a-z]", "lowercase letter"),
        (r"[A-Z]", "uppercase letter"),
        (r"\d", "number"),
        (r"[^A-Za-z0-9]", "symbol"),
    ]
    missing = [label for pattern, label in checks if not re.search(pattern, password)]
    if missing:
        raise ValueError(f"Password must include a {', '.join(missing)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_BYTES:
        return False
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def hash_password(password: str) -> str:
    validate_password_strength(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload: dict[str, Any] = {"sub": subject, "role": role, "type": "access", "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    return hmac.compare_digest(hash_token(token), token_hash)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid authentication token") from exc
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload
