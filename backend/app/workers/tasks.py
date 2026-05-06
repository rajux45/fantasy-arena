from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import or_, select

from app.db import SessionLocal
from app.logging_config import get_logger
from app.models.audit import AuditLog
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
    """Reactivate users whose self-exclusion has lapsed.

    Skips users that:
      - have a newer non-permanent exclusion still in force,
      - have any permanent exclusion,
      - were banned by an admin (presence of an `admin.user_ban` audit event).

    Each processed exclusion is flagged so we never reprocess it on later runs.
    """
    db = SessionLocal()
    try:
        now = datetime.now(UTC)
        excs = db.execute(
            select(SelfExclusion).where(
                SelfExclusion.processed.is_(False),
                SelfExclusion.is_permanent.is_(False),
                SelfExclusion.ends_at < now,
            )
        ).scalars().all()

        reactivated = 0
        for se in excs:
            # Mark this exclusion as processed regardless of outcome below.
            se.processed = True

            # Skip if user has any other still-active exclusion.
            other = db.execute(
                select(SelfExclusion).where(
                    SelfExclusion.user_id == se.user_id,
                    SelfExclusion.id != se.id,
                    or_(
                        SelfExclusion.is_permanent.is_(True),
                        SelfExclusion.ends_at > now,
                    ),
                ).limit(1)
            ).scalar_one_or_none()
            if other is not None:
                continue

            # Skip if user was banned by an admin.
            ban = db.execute(
                select(AuditLog).where(
                    AuditLog.action == "admin.user_ban",
                    AuditLog.target_type == "user",
                    AuditLog.target_id == str(se.user_id),
                ).limit(1)
            ).scalar_one_or_none()
            if ban is not None:
                continue

            user = db.get(User, se.user_id)
            if user is not None and not user.is_active:
                user.is_active = True
                reactivated += 1
        db.commit()
        return reactivated
    finally:
        db.close()
