"""Payment intent + webhook handling. Razorpay only for MVP; abstract for future gateways."""
from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass

from app.config import settings
from app.logging_config import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class CreatedOrder:
    order_id: str
    amount_paise: int
    currency: str = "INR"
    key_id: str = ""


def create_razorpay_order(amount_paise: int, receipt: str | None = None, notes: dict | None = None) -> CreatedOrder:
    """Create a Razorpay order. In dev (no keys) returns a fake one for plumbing tests."""
    receipt = receipt or f"fa_{uuid.uuid4().hex[:16]}"
    if settings.razorpay_key_id and settings.razorpay_key_secret:
        import razorpay  # local import to keep dev-only dependency optional

        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "notes": notes or {},
        })
        return CreatedOrder(order_id=order["id"], amount_paise=amount_paise, key_id=settings.razorpay_key_id)
    log.warning("razorpay_dev_stub", note="returning a fake order; configure keys for live")
    return CreatedOrder(order_id=f"order_dev_{uuid.uuid4().hex[:14]}", amount_paise=amount_paise, key_id="dev")


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    if not settings.razorpay_key_secret:
        return True  # dev allow
    expected = hmac.new(
        settings.razorpay_key_secret.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_signature(body_bytes: bytes, header_signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        return True
    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(),
        body_bytes,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, header_signature)
