from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.contest import Contest
from app.models.match import Match, MatchStatus
from app.models.player import Player
from app.models.sport import Sport, SportSlug
from app.schemas.contest import ContestOut, MatchOut, PlayerOut

router = APIRouter(prefix="/v1", tags=["matches"])


@router.get("/sports")
def list_sports(db: Session = Depends(get_db)):
    sports = db.execute(select(Sport).where(Sport.is_active.is_(True))).scalars().all()
    return [{"id": str(s.id), "slug": s.slug.value, "name": s.name} for s in sports]


@router.get("/matches", response_model=list[MatchOut])
def list_matches(
    sport: SportSlug | None = Query(default=None),
    status: MatchStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = select(Match, Sport).join(Sport, Match.sport_id == Sport.id)
    if sport is not None:
        q = q.where(Sport.slug == sport)
    if status is not None:
        q = q.where(Match.status == status)
    q = q.order_by(Match.starts_at.asc()).limit(100)

    rows = db.execute(q).all()
    return [
        MatchOut(
            id=m.id,
            sport=s.slug.value,
            short_name=m.short_name,
            home_team=m.home_team,
            away_team=m.away_team,
            venue=m.venue,
            starts_at=m.starts_at,
            lineup_locks_at=m.lineup_locks_at,
            status=m.status.value,
        )
        for m, s in rows
    ]


@router.get("/matches/{match_id}", response_model=MatchOut)
def get_match(match_id: UUID, db: Session = Depends(get_db)):
    m = db.get(Match, match_id)
    if m is None:
        raise HTTPException(404, "match not found")
    s = db.get(Sport, m.sport_id)
    return MatchOut(
        id=m.id,
        sport=s.slug.value if s else "",
        short_name=m.short_name,
        home_team=m.home_team,
        away_team=m.away_team,
        venue=m.venue,
        starts_at=m.starts_at,
        lineup_locks_at=m.lineup_locks_at,
        status=m.status.value,
    )


@router.get("/matches/{match_id}/players", response_model=list[PlayerOut])
def match_players(match_id: UUID, db: Session = Depends(get_db)):
    m = db.get(Match, match_id)
    if m is None:
        raise HTTPException(404, "match not found")
    players = db.execute(
        select(Player).where(
            Player.sport_id == m.sport_id,
            Player.team_name.in_([m.home_team, m.away_team]),
            Player.is_active.is_(True),
        )
    ).scalars().all()
    return [
        PlayerOut(
            id=p.id,
            full_name=p.full_name,
            short_name=p.short_name,
            team_name=p.team_name,
            role=p.role.value,
            credits=float(p.credits),
        )
        for p in players
    ]


@router.get("/matches/{match_id}/contests", response_model=list[ContestOut])
def match_contests(match_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Contest).where(Contest.match_id == match_id).order_by(Contest.entry_fee_paise.desc())
    ).scalars().all()
    return [
        ContestOut(
            id=c.id, name=c.name, kind=c.kind.value, status=c.status.value,
            entry_fee_paise=c.entry_fee_paise, prize_pool_paise=c.prize_pool_paise,
            total_slots=c.total_slots, filled_slots=c.filled_slots,
            max_teams_per_user=c.max_teams_per_user, is_private=c.is_private,
            invite_code=c.invite_code, guaranteed=c.guaranteed,
            rake_pct=float(c.rake_pct),
        )
        for c in rows
    ]
