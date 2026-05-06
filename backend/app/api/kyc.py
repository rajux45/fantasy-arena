from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.kyc import KycRecord
from app.models.user import KycStatus, User
from app.services.security import encrypt_pii

router = APIRouter(prefix="/v1/kyc", tags=["kyc"])


@router.post("/submit")
def submit_kyc(
    payload: dict = Body(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    aadhaar = (payload.get("aadhaar") or "").replace(" ", "")
    pan = (payload.get("pan") or "").upper()
    name_on_doc = payload.get("name_on_doc")
    selfie_url = payload.get("selfie_url")

    if len(aadhaar) != 12 or not aadhaar.isdigit():
        raise HTTPException(400, "invalid aadhaar")
    if len(pan) != 10:
        raise HTTPException(400, "invalid pan")

    rec = KycRecord(
        user_id=user.id,
        aadhaar_last4=aadhaar[-4:],
        aadhaar_enc=encrypt_pii(aadhaar),
        pan_enc=encrypt_pii(pan),
        name_on_doc=name_on_doc,
        selfie_url=selfie_url,
        vendor="manual",
        status="pending",
    )
    db.add(rec)
    user.kyc_status = KycStatus.pending
    db.commit()
    return {"id": str(rec.id), "status": rec.status}


@router.get("/me")
def my_kyc(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rec = db.execute(
        select(KycRecord).where(KycRecord.user_id == user.id).order_by(KycRecord.created_at.desc())
    ).scalar_one_or_none()
    if rec is None:
        return {"status": "none"}
    return {
        "id": str(rec.id),
        "status": rec.status,
        "aadhaar_last4": rec.aadhaar_last4,
        "name_on_doc": rec.name_on_doc,
        "rejection_reason": rec.rejection_reason,
        "vendor": rec.vendor,
        "user_kyc_status": user.kyc_status.value,
    }
