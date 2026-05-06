from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import UUID as PgUUID


class PlayerRole(enum.StrEnum):
    # cricket
    batsman = "batsman"
    bowler = "bowler"
    all_rounder = "all_rounder"
    wicket_keeper = "wicket_keeper"
    # football
    goalkeeper = "goalkeeper"
    defender = "defender"
    midfielder = "midfielder"
    forward = "forward"
    # kabaddi
    raider = "raider"
    defender_kabaddi = "defender_kabaddi"
    all_rounder_kabaddi = "all_rounder_kabaddi"
    # basketball
    point_guard = "point_guard"
    shooting_guard = "shooting_guard"
    small_forward = "small_forward"
    power_forward = "power_forward"
    center = "center"


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sports.id", ondelete="CASCADE"), nullable=False, index=True
    )

    full_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    team_name: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    role: Mapped[PlayerRole] = mapped_column(Enum(PlayerRole, name="player_role"), nullable=False)
    credits: Mapped[float] = mapped_column(Numeric(4, 1), default=8.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
