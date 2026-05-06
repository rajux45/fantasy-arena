from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import UUID as PgUUID


class ResponsibleGamingSettings(Base, TimestampMixin):
    __tablename__ = "rg_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_rg_user"),)

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    daily_deposit_limit_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    weekly_deposit_limit_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    monthly_deposit_limit_paise: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    daily_session_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reality_check_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    push_responsible_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SelfExclusion(Base, TimestampMixin):
    __tablename__ = "self_exclusions"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_permanent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scope: Mapped[str] = mapped_column(String(20), default="all", nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # True once the worker has processed expiry; prevents repeated reactivations.
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
