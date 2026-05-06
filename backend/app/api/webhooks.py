from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from app.services import payment_service

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("x-razorpay-signature", "")
    if not payment_service.verify_webhook_signature(body, sig):
        raise HTTPException(401, "invalid signature")
    try:
        data = json.loads(body.decode())
    except Exception as exc:
        raise HTTPException(400, "invalid json") from exc
    # In a full implementation, look up the payment by gateway_payment_id and
    # transition status. Logged here for the MVP.
    return {"event": data.get("event"), "ok": True}
