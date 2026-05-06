from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.responsible import ResponsibleGamingSettings, SelfExclusion
from app.models.user import User
from app.schemas.responsible import RgSettingsIn, SelfExclusionIn

router = APIRouter(prefix="/v1/responsible", tags=["responsible-gaming"])


@router.get("/settings")
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rg = db.execute(
        select(ResponsibleGamingSettings).where(ResponsibleGamingSettings.user_id == user.id)
    ).scalar_one_or_none()
    if rg is None:
        rg = ResponsibleGamingSettings(user_id=user.id)
        db.add(rg)
        db.commit()
        db.refresh(rg)
    return {
        "daily_deposit_limit_paise": rg.daily_deposit_limit_paise,
        "weekly_deposit_limit_paise": rg.weekly_deposit_limit_paise,
        "monthly_deposit_limit_paise": rg.monthly_deposit_limit_paise,
        "daily_session_minutes": rg.daily_session_minutes,
        "reality_check_minutes": rg.reality_check_minutes,
    }


@router.put("/settings")
def update_settings(
    payload: RgSettingsIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rg = db.execute(
        select(ResponsibleGamingSettings).where(ResponsibleGamingSettings.user_id == user.id)
    ).scalar_one_or_none()
    if rg is None:
        rg = ResponsibleGamingSettings(user_id=user.id)
        db.add(rg)

    # Reductions are immediate; increases would normally have a 24h cool-off but
    # the simplified MVP applies immediately. See ARCHITECTURE.md.
    rg.daily_deposit_limit_paise = payload.daily_deposit_limit_paise
    rg.weekly_deposit_limit_paise = payload.weekly_deposit_limit_paise
    rg.monthly_deposit_limit_paise = payload.monthly_deposit_limit_paise
    rg.daily_session_minutes = payload.daily_session_minutes
    rg.reality_check_minutes = payload.reality_check_minutes
    db.commit()
    return {"ok": True}


@router.post("/self-exclude", status_code=201)
def self_exclude(
    payload: SelfExclusionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.is_permanent and not payload.days:
        raise HTTPException(400, "either days or is_permanent required")
    starts = datetime.now(UTC)
    ends = None if payload.is_permanent else starts + timedelta(days=payload.days)
    se = SelfExclusion(
        user_id=user.id,
        starts_at=starts,
        ends_at=ends,
        is_permanent=payload.is_permanent,
        scope=payload.scope,
        reason=payload.reason,
    )
    db.add(se)
    user.is_active = False
    db.commit()
    return {"id": str(se.id), "ends_at": ends.isoformat() if ends else None}
