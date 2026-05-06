"""OTP service. In dev, OTPs are deterministic and logged. In prod, sent via MSG91/SMS."""
from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass

from app.config import settings
from app.logging_config import get_logger

log = get_logger(__name__)

OTP_TTL_SECONDS = 300


@dataclass(slots=True)
class OtpRecord:
    code: str
    expires_at: float


# In-memory store for dev. Replace with Redis in prod (`SET otp:{phone} val EX 300`).
_store: dict[str, OtpRecord] = {}


def _key(channel: str, target: str) -> str:
    return f"{channel}:{target.lower()}"


def generate_otp(channel: str, target: str) -> str:
    """Returns the OTP that was generated (and dispatched in prod)."""
    code = f"{secrets.randbelow(900000) + 100000:06d}" if settings.env != "development" else "123456"
    _store[_key(channel, target)] = OtpRecord(code=code, expires_at=time.time() + OTP_TTL_SECONDS)
    log.info("otp_generated", channel=channel, target=target, dev=settings.is_dev)
    # In production: dispatch_msg91(target, code)
    return code if settings.is_dev else "***"


def verify_otp(channel: str, target: str, code: str) -> bool:
    rec = _store.get(_key(channel, target))
    if rec is None:
        return False
    if rec.expires_at < time.time():
        _store.pop(_key(channel, target), None)
        return False
    ok = secrets.compare_digest(rec.code, code)
    if ok:
        _store.pop(_key(channel, target), None)
    return ok


def fingerprint(target: str) -> str:
    return hashlib.sha256(target.encode()).hexdigest()[:16]
