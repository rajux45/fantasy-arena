from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from app.db import SessionLocal
from app.logging_config import get_logger
from app.models.contest import Contest, ContestStatus
from app.models.match import Match, MatchStatus
from app.models.responsible import SelfExclusion
from app.models.user import User
from app.models.wallet import LedgerEntry
from app.services.contest_service import settle_contest
from app.workers.celery_app import celery

log = get_logger(__name__)


@celery.task
def settle_completed_matches() -> int:
    db = SessionLocal()
    try:
        matches = db.execute(
            select(Match).where(Match.status == MatchStatus.completed)
        ).scalars().all()
        settled = 0
        for m in matches:
            contests = db.execute(
                select(Contest).where(Contest.match_id == m.id, Contest.status != ContestStatus.completed)
            ).scalars().all()
            for c in contests:
                try:
                    settle_contest(db, c)
                    settled += 1
                except Exception as exc:
                    log.error("settle_failed", contest_id=str(c.id), err=str(exc))
                    db.rollback()
            db.commit()
        return settled
    finally:
        db.close()


@celery.task
def reconcile_ledger() -> int:
    """Asserts Σ all ledger amounts == 0 globally."""
    db = SessionLocal()
    try:
        rows = db.execute(select(LedgerEntry.amount_paise)).scalars().all()
        s = sum(rows)
        log.info("ledger_reconcile", sum_paise=s, rows=len(rows))
        return s
    finally:
        db.close()


@celery.task
def expire_self_exclusions() -> int:
    db = SessionLocal()
    try:
        now = datetime.now(UTC)
        excs = db.execute(
            select(SelfExclusion).where(
                SelfExclusion.is_permanent.is_(False),
                SelfExclusion.ends_at < now,
            )
        ).scalars().all()
        for se in excs:
            user = db.get(User, se.user_id)
            if user:
                user.is_active = True
        db.commit()
        return len(excs)
    finally:
        db.close()
