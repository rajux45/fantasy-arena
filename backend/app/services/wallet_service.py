"""Double-entry ledger. Source of truth for money movement."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import LedgerEntry, Pocket, Wallet


class LedgerError(Exception):
    """Raised when a transaction violates ledger invariants."""


@dataclass(frozen=True, slots=True)
class Leg:
    """One side of a posting."""

    account: str
    amount_paise: int  # signed: + credit, - debit
    user_id: uuid.UUID | None = None
    pocket: Pocket | None = None
    meta: dict[str, Any] | None = None


def post_txn(
    db: Session,
    *,
    kind: str,
    legs: list[Leg],
    txn_id: uuid.UUID | None = None,
) -> uuid.UUID:
    """Post a transaction. All legs must sum to zero. Updates wallet aggregates atomically."""

    if not legs:
        raise LedgerError("transaction must have at least one leg")
    total = sum(leg.amount_paise for leg in legs)
    if total != 0:
        raise LedgerError(f"legs do not balance: sum={total}")

    txn_id = txn_id or uuid.uuid4()

    # 1) write ledger rows
    for leg in legs:
        db.add(
            LedgerEntry(
                txn_id=txn_id,
                user_id=leg.user_id,
                account=leg.account,
                pocket=leg.pocket,
                amount_paise=leg.amount_paise,
                kind=kind,
                meta=leg.meta or {},
            )
        )

    # 2) reflect in wallet aggregates (only legs scoped to a user pocket)
    for leg in legs:
        if leg.user_id is None:
            continue
        wallet = db.execute(
            select(Wallet).where(Wallet.user_id == leg.user_id).with_for_update()
        ).scalar_one_or_none()
        if wallet is None:
            wallet = Wallet(user_id=leg.user_id)
            db.add(wallet)
            db.flush()
            db.refresh(wallet)

        if leg.pocket == Pocket.deposit:
            wallet.deposit_paise = wallet.deposit_paise + leg.amount_paise
        elif leg.pocket == Pocket.winnings:
            wallet.winnings_paise = wallet.winnings_paise + leg.amount_paise
        elif leg.pocket == Pocket.bonus:
            wallet.bonus_paise = wallet.bonus_paise + leg.amount_paise
        elif leg.pocket is None and leg.account.startswith(f"casino_coins:{leg.user_id}"):
            wallet.casino_coins = wallet.casino_coins + leg.amount_paise

        if (
            wallet.deposit_paise < 0
            or wallet.winnings_paise < 0
            or wallet.bonus_paise < 0
            or wallet.casino_coins < 0
        ):
            raise LedgerError("insufficient funds")

    db.flush()
    return txn_id


def credit_casino_coins(db: Session, *, user_id: uuid.UUID, coins: int, kind: str, meta: dict | None = None) -> uuid.UUID:
    return post_txn(
        db,
        kind=kind,
        legs=[
            Leg(account=f"casino_coins:{user_id}", amount_paise=coins, user_id=user_id, meta=meta),
            Leg(account="system:casino_pool", amount_paise=-coins, meta=meta),
        ],
    )


def debit_casino_coins(db: Session, *, user_id: uuid.UUID, coins: int, kind: str, meta: dict | None = None) -> uuid.UUID:
    return post_txn(
        db,
        kind=kind,
        legs=[
            Leg(account=f"casino_coins:{user_id}", amount_paise=-coins, user_id=user_id, meta=meta),
            Leg(account="system:casino_pool", amount_paise=coins, meta=meta),
        ],
    )


def get_wallet(db: Session, user_id: uuid.UUID) -> Wallet:
    wallet = db.execute(select(Wallet).where(Wallet.user_id == user_id)).scalar_one_or_none()
    if wallet is None:
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
        db.flush()
        db.refresh(wallet)
    return wallet


def total_balance_paise(wallet: Wallet) -> int:
    return wallet.deposit_paise + wallet.winnings_paise + wallet.bonus_paise


def withdrawable_paise(wallet: Wallet) -> int:
    """Only `deposit` (unused) + `winnings` are withdrawable. Bonus is play-only. Casino coins never."""
    return wallet.deposit_paise + wallet.winnings_paise


def assert_ledger_balances(db: Session, txn_id: uuid.UUID) -> None:
    """Defensive check used in tests."""
    rows = db.execute(
        select(LedgerEntry.amount_paise).where(LedgerEntry.txn_id == txn_id)
    ).scalars().all()
    if sum(rows) != 0:
        raise LedgerError(f"ledger imbalance for txn {txn_id}: sum={sum(rows)}")
