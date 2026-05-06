from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1/tournaments", tags=["tournaments"])


class Tournament(BaseModel):
    id: str
    name: str
    sport: str
    status: str
    prize_pool_paise: int
    starts_at: str | None = None
    ends_at: str | None = None


_STATIC_TOURNAMENTS = [
    Tournament(id="t-ipl-26", name="IPL 2026", sport="cricket", status="live", prize_pool_paise=500_000_00 * 100),
    Tournament(id="t-isl-26", name="ISL 2026", sport="football", status="live", prize_pool_paise=150_000_00 * 100),
    Tournament(id="t-pkl-26", name="PKL 2026", sport="kabaddi", status="upcoming", prize_pool_paise=50_000_00 * 100),
    Tournament(id="t-nba-26", name="NBA Finals 2026", sport="basketball", status="upcoming", prize_pool_paise=25_000_00 * 100),
]


@router.get("", response_model=list[Tournament])
def list_tournaments(sport: str | None = None, status: str | None = None) -> list[Tournament]:
    out = _STATIC_TOURNAMENTS
    if sport:
        out = [t for t in out if t.sport == sport]
    if status:
        out = [t for t in out if t.status == status]
    return list(out)


@router.get("/{tournament_id}", response_model=Tournament)
def detail(tournament_id: str) -> Tournament | None:
    for t in _STATIC_TOURNAMENTS:
        if t.id == tournament_id:
            return t
    return None
