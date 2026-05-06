from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import UUID as PgUUID
from app.models.wallet import SqliteFriendlyBigInt


class UserTeam(Base, TimestampMixin):
    __tablename__ = "user_teams"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    captain_player_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("players.id", ondelete="RESTRICT"), nullable=False
    )
    vice_captain_player_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("players.id", ondelete="RESTRICT"), nullable=False
    )
    total_credits: Mapped[float] = mapped_column(Numeric(5, 1), default=0, nullable=False)
    points: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class UserTeamPlayer(Base):
    __tablename__ = "user_team_players"
    __table_args__ = (
        UniqueConstraint("team_id", "player_id", name="uq_utp_team_player"),
    )

    id: Mapped[int] = mapped_column(SqliteFriendlyBigInt, primary_key=True, autoincrement=True)
    team_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("user_teams.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("players.id", ondelete="RESTRICT"), nullable=False
    )
    position: Mapped[str | None] = mapped_column(String(20), nullable=True)
