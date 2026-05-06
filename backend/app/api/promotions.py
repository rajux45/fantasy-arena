from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.promo import PromoCode
from app.models.user import User

router = APIRouter(prefix="/v1/promotions", tags=["promotions"])


class PromoOut(BaseModel):
    code: str
    kind: str
    value_paise: int
    value_pct: float
    min_deposit_paise: int
    max_bonus_paise: int
    ends_at: str | None


@router.get("", response_model=list[PromoOut])
def list_active(db: Session = Depends(get_db)):
    now = datetime.now(UTC)
    rows = db.execute(
        select(PromoCode).where(PromoCode.is_active.is_(True))
    ).scalars().all()
    out: list[PromoOut] = []
    for p in rows:
        if p.ends_at and p.ends_at < now:
            continue
        if p.starts_at and p.starts_at > now:
            continue
        out.append(PromoOut(
            code=p.code,
            kind=str(p.kind),
            value_paise=p.value_paise,
            value_pct=float(p.value_pct or 0),
            min_deposit_paise=p.min_deposit_paise,
            max_bonus_paise=p.max_bonus_paise,
            ends_at=p.ends_at.isoformat() if p.ends_at else None,
        ))
    return out


class ApplyPromoIn(BaseModel):
    code: str
    deposit_paise: int


@router.post("/apply")
def preview_apply(
    body: ApplyPromoIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    promo = db.execute(select(PromoCode).where(PromoCode.code == body.code)).scalar_one_or_none()
    if promo is None or not promo.is_active:
        raise HTTPException(404, "promo code not found or inactive")
    if body.deposit_paise < promo.min_deposit_paise:
        raise HTTPException(400, f"min deposit ₹{promo.min_deposit_paise / 100:.2f}")
    bonus = 0
    if str(promo.kind) == "deposit_match":
        bonus = int(body.deposit_paise * (float(promo.value_pct) / 100))
    elif str(promo.kind) == "flat_bonus":
        bonus = promo.value_paise
    if promo.max_bonus_paise:
        bonus = min(bonus, promo.max_bonus_paise)
    return {"code": promo.code, "bonus_paise": bonus, "deposit_paise": body.deposit_paise}
