from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserAdminRow(BaseModel):
    id: UUID
    email: str | None
    phone: str | None
    full_name: str | None
    role: str
    kyc_status: str
    state_code: str | None
    is_active: bool
    created_at: datetime


class WithdrawalApproveIn(BaseModel):
    note: str | None = None


class WithdrawalRejectIn(BaseModel):
    reason: str


class KycReviewIn(BaseModel):
    approve: bool
    reason: str | None = None


class ManualWalletAdjust(BaseModel):
    user_id: UUID
    pocket: str  # deposit | winnings | bonus
    amount_paise: int  # signed
    reason: str
