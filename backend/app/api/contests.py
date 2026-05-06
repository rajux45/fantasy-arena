from __future__ import annotations

from decimal import ROUND_DOWN, Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, get_request_meta
from app.models.contest import Contest, ContestEntry, ContestKind, ContestStatus
from app.models.match import Match
from app.models.team import UserTeam
from app.models.user import User
from app.schemas.contest import (
    ContestEntryOut,
    ContestJoin,
    ContestOut,
    PrivateContestCreate,
)
from app.services.audit_service import write_audit
from app.services.contest_service import ContestError, join_contest
from app.services.security import gen_invite_code

router = APIRouter(prefix="/v1/contests", tags=["contests"])


@router.get("/{contest_id}", response_model=ContestOut)
def get_contest(contest_id: UUID, db: Session = Depends(get_db)):
    c = db.get(Contest, contest_id)
    if c is None:
        raise HTTPException(404, "contest not found")
    return ContestOut(
        id=c.id, name=c.name, kind=c.kind.value, status=c.status.value,
        entry_fee_paise=c.entry_fee_paise, prize_pool_paise=c.prize_pool_paise,
        total_slots=c.total_slots, filled_slots=c.filled_slots,
        max_teams_per_user=c.max_teams_per_user, is_private=c.is_private,
        invite_code=c.invite_code, guaranteed=c.guaranteed,
        rake_pct=float(c.rake_pct),
    )


@router.post("/{contest_id}/join", response_model=ContestEntryOut, status_code=201)
def join(
    contest_id: UUID,
    payload: ContestJoin,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    contest = db.get(Contest, contest_id)
    if contest is None:
        raise HTTPException(404, "contest not found")
    team = db.get(UserTeam, payload.team_id)
    if team is None:
        raise HTTPException(404, "team not found")
    try:
        receipt = join_contest(db, user=user, contest=contest, team=team)
    except ContestError as exc:
        raise HTTPException(400, str(exc)) from exc
    entry = db.get(ContestEntry, receipt.entry_id)
    write_audit(
        db, actor_user_id=user.id, action="contest.joined",
        target_type="contest", target_id=str(contest_id),
        meta={"entry_id": str(entry.id), "fee_paise": receipt.entry_fee_paise}, **meta,
    )
    db.commit()
    return ContestEntryOut(
        id=entry.id, contest_id=entry.contest_id, user_id=entry.user_id,
        team_id=entry.team_id, points=float(entry.points), rank=entry.rank,
        payout_paise=entry.payout_paise,
    )


@router.get("/{contest_id}/leaderboard", response_model=list[ContestEntryOut])
def leaderboard(contest_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(ContestEntry).where(ContestEntry.contest_id == contest_id)
        .order_by(ContestEntry.points.desc(), ContestEntry.created_at.asc())
        .limit(100)
    ).scalars().all()
    return [
        ContestEntryOut(
            id=e.id, contest_id=e.contest_id, user_id=e.user_id, team_id=e.team_id,
            points=float(e.points), rank=e.rank, payout_paise=e.payout_paise,
        )
        for e in rows
    ]


@router.post("/private", response_model=ContestOut, status_code=201)
def create_private(
    payload: PrivateContestCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, payload.match_id)
    if match is None:
        raise HTTPException(404, "match not found")
    # Decimal arithmetic for paise; floor to integer paise (rake takes the residue).
    rake = Decimal(str(payload.rake_pct))
    gross = Decimal(payload.entry_fee_paise) * Decimal(payload.total_slots)
    prize_pool = int(
        (gross * (Decimal(100) - rake) / Decimal(100)).quantize(Decimal(1), rounding=ROUND_DOWN)
    )
    c = Contest(
        match_id=match.id,
        name=payload.name,
        kind=ContestKind.private,
        status=ContestStatus.open,
        entry_fee_paise=payload.entry_fee_paise,
        prize_pool_paise=prize_pool,
        max_teams_per_user=payload.max_teams_per_user,
        total_slots=payload.total_slots,
        is_private=True,
        invite_code=gen_invite_code(),
        creator_user_id=user.id,
        rake_pct=payload.rake_pct,
    )
    db.add(c)
    db.commit()
    return ContestOut(
        id=c.id, name=c.name, kind=c.kind.value, status=c.status.value,
        entry_fee_paise=c.entry_fee_paise, prize_pool_paise=c.prize_pool_paise,
        total_slots=c.total_slots, filled_slots=c.filled_slots,
        max_teams_per_user=c.max_teams_per_user, is_private=c.is_private,
        invite_code=c.invite_code, guaranteed=c.guaranteed,
        rake_pct=float(c.rake_pct),
    )


@router.get("/private/by-code/{code}", response_model=ContestOut)
def find_private(code: str, db: Session = Depends(get_db)):
    c = db.execute(
        select(Contest).where(Contest.invite_code == code.upper())
    ).scalar_one_or_none()
    if c is None:
        raise HTTPException(404, "contest not found")
    return ContestOut(
        id=c.id, name=c.name, kind=c.kind.value, status=c.status.value,
        entry_fee_paise=c.entry_fee_paise, prize_pool_paise=c.prize_pool_paise,
        total_slots=c.total_slots, filled_slots=c.filled_slots,
        max_teams_per_user=c.max_teams_per_user, is_private=c.is_private,
        invite_code=c.invite_code, guaranteed=c.guaranteed,
        rake_pct=float(c.rake_pct),
    )
