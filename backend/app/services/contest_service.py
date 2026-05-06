"""Contest join + payout logic."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contest import Contest, ContestEntry, ContestStatus, PrizeSlab
from app.models.match import Match, MatchStatus
from app.models.team import UserTeam
from app.models.user import User
from app.models.wallet import Pocket
from app.services import wallet_service
from app.services.geo_service import is_fantasy_real_money_allowed
from app.services.tax_service import compute_gst_on_entry


class ContestError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class JoinReceipt:
    entry_id: uuid.UUID
    txn_id: uuid.UUID
    entry_fee_paise: int
    gst_paise: int


def join_contest(
    db: Session,
    *,
    user: User,
    contest: Contest,
    team: UserTeam,
) -> JoinReceipt:
    if contest.status not in {ContestStatus.open}:
        raise ContestError("contest is not open")
    match: Match | None = db.get(Match, contest.match_id)
    if match is None or match.status != MatchStatus.upcoming:
        raise ContestError("match no longer accepting entries")

    # Geo block for paid contests only.
    if contest.entry_fee_paise > 0 and not is_fantasy_real_money_allowed(user.state_code):
        raise ContestError(
            f"real-money fantasy contests are not available in your state ({user.state_code})"
        )

    if team.user_id != user.id or team.match_id != contest.match_id:
        raise ContestError("team / contest mismatch")

    # Per-user team-count limit
    existing_count = db.execute(
        select(ContestEntry).where(
            ContestEntry.contest_id == contest.id, ContestEntry.user_id == user.id
        )
    ).scalars().all()
    if len(existing_count) >= contest.max_teams_per_user:
        raise ContestError("max teams per user exceeded for this contest")

    if contest.filled_slots >= contest.total_slots:
        raise ContestError("contest is full")

    fee = contest.entry_fee_paise
    gst = compute_gst_on_entry(fee) if fee > 0 else 0

    txn_id: uuid.UUID | None = None
    if fee > 0:
        wallet = wallet_service.get_wallet(db, user.id)
        usable = wallet.deposit_paise + wallet.bonus_paise + wallet.winnings_paise
        if usable < fee:
            raise ContestError("insufficient wallet balance")

        # Pocket priority: bonus -> deposit -> winnings (configurable).
        bonus_used = min(wallet.bonus_paise, fee)
        deposit_used = min(wallet.deposit_paise, fee - bonus_used)
        winnings_used = fee - bonus_used - deposit_used

        legs = []
        if bonus_used:
            legs.append(wallet_service.Leg(account=f"user:{user.id}:bonus", amount_paise=-bonus_used,
                                           user_id=user.id, pocket=Pocket.bonus))
        if deposit_used:
            legs.append(wallet_service.Leg(account=f"user:{user.id}:deposit", amount_paise=-deposit_used,
                                           user_id=user.id, pocket=Pocket.deposit))
        if winnings_used:
            legs.append(wallet_service.Leg(account=f"user:{user.id}:winnings",
                                           amount_paise=-winnings_used, user_id=user.id, pocket=Pocket.winnings))

        legs.append(wallet_service.Leg(
            account=f"system:contest_pool:{contest.id}", amount_paise=fee - gst,
            meta={"contest_id": str(contest.id)},
        ))
        if gst:
            legs.append(wallet_service.Leg(account="system:gst_payable", amount_paise=gst))

        txn_id = wallet_service.post_txn(db, kind="contest.join", legs=legs)

    entry = ContestEntry(
        contest_id=contest.id, user_id=user.id, team_id=team.id, txn_id=txn_id
    )
    db.add(entry)
    contest.filled_slots = contest.filled_slots + 1
    if contest.filled_slots >= contest.total_slots:
        contest.status = ContestStatus.full
    db.flush()

    return JoinReceipt(entry_id=entry.id, txn_id=txn_id or uuid.UUID(int=0),
                        entry_fee_paise=fee, gst_paise=gst)


def settle_contest(db: Session, contest: Contest) -> dict:
    """Compute ranks + payouts. Idempotent only if called once per contest (use Celery lock)."""
    if contest.status not in {ContestStatus.open, ContestStatus.full, ContestStatus.locked, ContestStatus.settling}:
        raise ContestError(f"cannot settle contest in status {contest.status}")
    contest.status = ContestStatus.settling
    db.flush()

    entries: list[ContestEntry] = db.execute(
        select(ContestEntry).where(ContestEntry.contest_id == contest.id)
    ).scalars().all()
    entries.sort(key=lambda e: (-(float(e.points or 0)), e.created_at))

    slabs: list[PrizeSlab] = db.execute(
        select(PrizeSlab).where(PrizeSlab.contest_id == contest.id).order_by(PrizeSlab.rank_from.asc())
    ).scalars().all()

    summary: dict = {"winners": 0, "total_paid_paise": 0}
    for idx, entry in enumerate(entries, start=1):
        entry.rank = idx
        prize = 0
        for slab in slabs:
            if slab.rank_from <= idx <= slab.rank_to:
                prize = slab.prize_paise
                break
        if prize > 0:
            wallet_service.post_txn(
                db,
                kind="contest.payout",
                legs=[
                    wallet_service.Leg(
                        account=f"system:contest_pool:{contest.id}", amount_paise=-prize,
                        meta={"contest_id": str(contest.id), "entry_id": str(entry.id)},
                    ),
                    wallet_service.Leg(
                        account=f"user:{entry.user_id}:winnings", amount_paise=prize,
                        user_id=entry.user_id, pocket=Pocket.winnings,
                    ),
                ],
            )
            entry.payout_paise = prize
            summary["winners"] += 1
            summary["total_paid_paise"] += prize

    contest.status = ContestStatus.completed
    db.flush()
    return summary
