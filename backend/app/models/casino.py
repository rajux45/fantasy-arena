from __future__ import annotations

import enum
import uuid

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class CasinoGameSlug(enum.StrEnum):
    crash = "crash"
    plinko = "plinko"
    mines = "mines"
    dice = "dice"
    roulette = "roulette"
    slots = "slots"
    blackjack = "blackjack"


class CasinoGame(Base, TimestampMixin):
    __tablename__ = "casino_games"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[CasinoGameSlug] = mapped_column(
        Enum(CasinoGameSlug, name="casino_game_slug"), nullable=False, unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    house_edge_bp: Mapped[int] = mapped_column(Integer, default=200, nullable=False)  # basis points
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class CasinoSeed(Base, TimestampMixin):
    __tablename__ = "casino_seeds"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    server_seed: Mapped[str | None] = mapped_column(String(128), nullable=True)
    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    client_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    nonce: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    is_revealed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class CasinoRound(Base, TimestampMixin):
    __tablename__ = "casino_rounds"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    game_slug: Mapped[CasinoGameSlug] = mapped_column(
        Enum(CasinoGameSlug, name="casino_game_slug_round"), nullable=False, index=True
    )

    bet_coins: Mapped[int] = mapped_column(BigInteger, nullable=False)
    payout_coins: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    multiplier: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)

    server_seed_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    server_seed: Mapped[str | None] = mapped_column(String(128), nullable=True)
    client_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    nonce: Mapped[int] = mapped_column(BigInteger, nullable=False)

    outcome: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    bet_input: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
