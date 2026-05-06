from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MatchOut(BaseModel):
    id: UUID
    sport: str
    short_name: str
    home_team: str
    away_team: str
    venue: str | None
    starts_at: datetime
    lineup_locks_at: datetime
    status: str


class PlayerOut(BaseModel):
    id: UUID
    full_name: str
    short_name: str | None
    team_name: str
    role: str
    credits: float


class ContestOut(BaseModel):
    id: UUID
    name: str
    kind: str
    status: str
    entry_fee_paise: int
    prize_pool_paise: int
    total_slots: int
    filled_slots: int
    max_teams_per_user: int
    is_private: bool
    invite_code: str | None
    guaranteed: bool
    rake_pct: float


class TeamCreate(BaseModel):
    match_id: UUID
    name: str = Field(min_length=2, max_length=60)
    player_ids: list[UUID]
    captain_player_id: UUID
    vice_captain_player_id: UUID


class TeamOut(BaseModel):
    id: UUID
    user_id: UUID
    match_id: UUID
    name: str
    captain_player_id: UUID
    vice_captain_player_id: UUID
    total_credits: float
    points: float
    is_locked: bool
    player_ids: list[UUID]


class ContestJoin(BaseModel):
    team_id: UUID
    idempotency_key: str | None = None


class ContestEntryOut(BaseModel):
    id: UUID
    contest_id: UUID
    user_id: UUID
    team_id: UUID
    points: float
    rank: int | None
    payout_paise: int


class PrivateContestCreate(BaseModel):
    match_id: UUID
    name: str
    entry_fee_paise: int = Field(ge=0)
    total_slots: int = Field(ge=2, le=200)
    max_teams_per_user: int = Field(ge=1, le=20, default=1)
    rake_pct: float = Field(ge=0, le=25, default=10)
