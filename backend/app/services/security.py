from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Bcrypt has a 72-byte limit; we hash the password with sha-256 first to bypass it safely.
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prep_password(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    return _pwd.hash(_prep_password(password).decode())


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _pwd.verify(_prep_password(password).decode(), hashed)
    except Exception:
        return False


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_min),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str, jti: str | None = None) -> tuple[str, str]:
    now = datetime.now(UTC)
    jti = jti or secrets.token_urlsafe(24)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_ttl_days),
        "type": "refresh",
        "jti": jti,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm), jti


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("invalid_token") from exc


def hmac_sha256_hex(key: str, msg: str) -> str:
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def gen_referral_code(length: int = 8) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def gen_invite_code(length: int = 6) -> str:
    return gen_referral_code(length)


def gen_uuid() -> uuid.UUID:
    return uuid.uuid4()


def _fernet() -> Fernet | None:
    key = settings.pii_encryption_key.strip()
    if not key:
        return None
    if len(key) < 44:  # not a Fernet key, derive one
        key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()).decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_pii(plaintext: str | None) -> str | None:
    if plaintext is None:
        return None
    f = _fernet()
    if f is None:
        return plaintext  # dev fallback
    return f.encrypt(plaintext.encode()).decode()


def decrypt_pii(ciphertext: str | None) -> str | None:
    if ciphertext is None:
        return None
    f = _fernet()
    if f is None:
        return ciphertext
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        return None
