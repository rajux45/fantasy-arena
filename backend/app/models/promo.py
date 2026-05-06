from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class PromoKind(enum.StrEnum):
    deposit_match = "deposit_match"
    flat_bonus = "flat_bonus"
    cashback = "cashback"
    free_entry = "free_entry"


class PromoCode(Base, TimestampMixin):
    __tablename__ = "promo_codes"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    kind: Mapped[PromoKind] = mapped_column(Enum(PromoKind, name="promo_kind"), nullable=False)

    value_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    value_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    min_deposit_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    max_bonus_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class CashbackRule(Base, TimestampMixin):
    __tablename__ = "cashback_rules"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    threshold_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cashback_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    cap_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    period: Mapped[str] = mapped_column(String(10), default="weekly", nullable=False)  # daily/weekly/monthly
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Referral(Base, TimestampMixin):
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    referee_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    first_deposit_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    bonus_paid_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    lifetime_commission_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
