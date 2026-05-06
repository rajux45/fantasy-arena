from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.match import Match, MatchStatus
from app.models.sport import Sport
from app.models.team import UserTeam, UserTeamPlayer
from app.models.user import User
from app.schemas.contest import TeamCreate, TeamOut
from app.services.team_service import validate_team

router = APIRouter(prefix="/v1/teams", tags=["teams"])


def _team_to_out(t: UserTeam, db: Session) -> TeamOut:
    pids = [p.player_id for p in db.execute(
        select(UserTeamPlayer).where(UserTeamPlayer.team_id == t.id)
    ).scalars().all()]
    return TeamOut(
        id=t.id,
        user_id=t.user_id,
        match_id=t.match_id,
        name=t.name,
        captain_player_id=t.captain_player_id,
        vice_captain_player_id=t.vice_captain_player_id,
        total_credits=float(t.total_credits or 0),
        points=float(t.points or 0),
        is_locked=t.is_locked,
        player_ids=pids,
    )


@router.post("", response_model=TeamOut, status_code=201)
def create_team(
    payload: TeamCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, payload.match_id)
    if match is None:
        raise HTTPException(404, "match not found")
    if match.status != MatchStatus.upcoming:
        raise HTTPException(400, "team creation closed for this match")

    sport = db.get(Sport, match.sport_id)
    if sport is None:
        raise HTTPException(500, "sport not found")

    v = validate_team(
        db,
        sport=sport.slug,
        player_ids=payload.player_ids,
        captain_id=payload.captain_player_id,
        vice_captain_id=payload.vice_captain_player_id,
    )
    if not v.ok:
        raise HTTPException(400, v.error or "invalid team")

    t = UserTeam(
        user_id=user.id,
        match_id=match.id,
        name=payload.name,
        captain_player_id=payload.captain_player_id,
        vice_captain_player_id=payload.vice_captain_player_id,
        total_credits=v.total_credits,
    )
    db.add(t)
    db.flush()
    for pid in payload.player_ids:
        db.add(UserTeamPlayer(team_id=t.id, player_id=pid))
    db.commit()
    return _team_to_out(t, db)


@router.get("/match/{match_id}", response_model=list[TeamOut])
def my_match_teams(
    match_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    teams = db.execute(
        select(UserTeam).where(UserTeam.user_id == user.id, UserTeam.match_id == match_id)
    ).scalars().all()
    return [_team_to_out(t, db) for t in teams]


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.get(UserTeam, team_id)
    if t is None or t.user_id != user.id:
        raise HTTPException(404, "team not found")
    return _team_to_out(t, db)
