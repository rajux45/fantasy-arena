from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class MatchStatus(enum.StrEnum):
    upcoming = "upcoming"
    live = "live"
    completed = "completed"
    cancelled = "cancelled"


class Match(Base, TimestampMixin):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    sport_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sports.id", ondelete="CASCADE"), nullable=False, index=True,
    )

    short_name: Mapped[str] = mapped_column(String(60), nullable=False)
    home_team: Mapped[str] = mapped_column(String(60), nullable=False)
    away_team: Mapped[str] = mapped_column(String(60), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(120), nullable=True)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    lineup_locks_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"),
        default=MatchStatus.upcoming,
        nullable=False,
        index=True,
    )
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    raw_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class MatchPlayerStats(Base, TimestampMixin):
    __tablename__ = "match_player_stats"
    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_mps_match_player"),)

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )

    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    fantasy_points: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=0)
