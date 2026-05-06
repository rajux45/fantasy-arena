from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class ContestKind(enum.StrEnum):
    mega = "mega"
    head_to_head = "head_to_head"
    small = "small"
    practice = "practice"
    private = "private"


class ContestStatus(enum.StrEnum):
    open = "open"
    full = "full"
    locked = "locked"
    settling = "settling"
    completed = "completed"
    cancelled = "cancelled"


class Contest(Base, TimestampMixin):
    __tablename__ = "contests"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[ContestKind] = mapped_column(
        Enum(ContestKind, name="contest_kind"), default=ContestKind.mega, nullable=False
    )
    status: Mapped[ContestStatus] = mapped_column(
        Enum(ContestStatus, name="contest_status"),
        default=ContestStatus.open,
        nullable=False,
        index=True,
    )

    entry_fee_paise: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    prize_pool_paise: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    max_teams_per_user: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    filled_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    guaranteed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    invite_code: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    creator_user_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    prize_slabs: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    rake_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=18.0, nullable=False)


class PrizeSlab(Base):
    __tablename__ = "prize_slabs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    contest_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    rank_from: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_to: Mapped[int] = mapped_column(Integer, nullable=False)
    prize_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)


class ContestEntry(Base, TimestampMixin):
    __tablename__ = "contest_entries"
    __table_args__ = (
        UniqueConstraint("contest_id", "team_id", name="uq_entry_contest_team"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contest_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("user_teams.id", ondelete="CASCADE"), nullable=False
    )
    txn_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    points: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payout_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
