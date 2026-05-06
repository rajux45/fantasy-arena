from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.promo import Referral
from app.models.user import User

router = APIRouter(prefix="/v1/referrals", tags=["referrals"])


def _code_for(user: User) -> str:
    h = hashlib.sha256(str(user.id).encode()).hexdigest().upper()
    return f"FA-{h[:4]}-{h[4:8]}"


class MyReferral(BaseModel):
    code: str
    link: str
    total_referees: int
    total_commission_paise: int


@router.get("/me", response_model=MyReferral)
def my_referral(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = _code_for(user)
    total = db.execute(
        select(func.count()).select_from(Referral).where(Referral.referrer_user_id == user.id)
    ).scalar_one()
    commission = db.execute(
        select(func.coalesce(func.sum(Referral.lifetime_commission_paise), 0))
        .where(Referral.referrer_user_id == user.id)
    ).scalar_one()
    return MyReferral(
        code=code,
        link=f"https://fantasy-arena.in/r/{code}",
        total_referees=int(total or 0),
        total_commission_paise=int(commission or 0),
    )


class ReferreeRow(BaseModel):
    referee_user_id: str
    first_deposit_paise: int
    bonus_paid_paise: int
    lifetime_commission_paise: int


@router.get("/list", response_model=list[ReferreeRow])
def list_referees(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    rows = db.execute(
        select(Referral)
        .where(Referral.referrer_user_id == user.id)
        .order_by(desc(Referral.created_at))
        .limit(min(limit, 200))
    ).scalars().all()
    return [
        ReferreeRow(
            referee_user_id=str(r.referee_user_id),
            first_deposit_paise=r.first_deposit_paise,
            bonus_paid_paise=r.bonus_paid_paise,
            lifetime_commission_paise=r.lifetime_commission_paise,
        )
        for r in rows
    ]
