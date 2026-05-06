from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.contest import ContestEntry
from app.models.team import UserTeam

router = APIRouter(prefix="/v1/leaderboard", tags=["leaderboard"])


class LeaderboardRow(BaseModel):
    rank: int
    user_id: str
    team_id: str
    points: float


@router.get("/contest/{contest_id}", response_model=list[LeaderboardRow])
def contest_leaderboard(
    contest_id: str,
    db: Session = Depends(get_db),
    limit: int = 100,
):
    rows = db.execute(
        select(ContestEntry, UserTeam)
        .join(UserTeam, ContestEntry.team_id == UserTeam.id)
        .where(ContestEntry.contest_id == contest_id)
        .order_by(desc(UserTeam.points))
        .limit(min(limit, 500))
    ).all()
    if not rows:
        raise HTTPException(404, "no entries for this contest yet")
    return [
        LeaderboardRow(rank=i + 1, user_id=str(e.user_id), team_id=str(t.id), points=float(t.points))
        for i, (e, t) in enumerate(rows)
    ]
