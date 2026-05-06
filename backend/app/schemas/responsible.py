from __future__ import annotations

from pydantic import BaseModel, Field


class RgSettingsIn(BaseModel):
    daily_deposit_limit_paise: int | None = Field(default=None, ge=0)
    weekly_deposit_limit_paise: int | None = Field(default=None, ge=0)
    monthly_deposit_limit_paise: int | None = Field(default=None, ge=0)
    daily_session_minutes: int | None = Field(default=None, ge=0)
    reality_check_minutes: int = Field(default=30, ge=5, le=240)


class SelfExclusionIn(BaseModel):
    days: int | None = Field(default=None, ge=1, le=3650)
    is_permanent: bool = False
    scope: str = Field(default="all", pattern="^(all|fantasy|casino)$")
    reason: str | None = None
