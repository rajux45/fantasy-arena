from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)

# SQLite needs INTEGER for AUTOINCREMENT primary keys; BigInteger works on Postgres.
SqliteFriendlyBigInt = BigInteger().with_variant(Integer, "sqlite")
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class Pocket(enum.StrEnum):
    deposit = "deposit"
    winnings = "winnings"
    bonus = "bonus"


class Wallet(Base, TimestampMixin):
    """Aggregate wallet rolled up from ledger. Source of truth = ledger."""

    __tablename__ = "wallets"
    __table_args__ = (UniqueConstraint("user_id", name="uq_wallets_user"),)

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # All money values are stored in paise (₹1 = 100 paise) as bigint to avoid float.
    deposit_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    winnings_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    bonus_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    casino_coins: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)


class LedgerEntry(Base):
    """Double-entry ledger row. Σ amounts within a txn_id MUST equal zero."""

    __tablename__ = "ledger_entries"
    __table_args__ = (
        Index("ix_ledger_txn", "txn_id"),
        Index("ix_ledger_account", "account"),
        Index("ix_ledger_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(SqliteFriendlyBigInt, primary_key=True, autoincrement=True)
    txn_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    account: Mapped[str] = mapped_column(String(120), nullable=False)
    pocket: Mapped[Pocket | None] = mapped_column(
        Enum(Pocket, name="ledger_pocket"), nullable=True
    )

    # signed amount: positive = credit to this account, negative = debit
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)

    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class PaymentStatus(enum.StrEnum):
    created = "created"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_payments_idem"),
        UniqueConstraint("gateway_order_id", name="uq_payments_gateway_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    gateway: Mapped[str] = mapped_column(String(20), nullable=False, default="razorpay")
    gateway_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gateway_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    idempotency_key: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    gst_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    net_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    purpose: Mapped[str] = mapped_column(String(20), default="deposit", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.created,
        nullable=False,
        index=True,
    )
    raw_webhook: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class WithdrawalStatus(enum.StrEnum):
    requested = "requested"
    in_review = "in_review"
    approved = "approved"
    payout_initiated = "payout_initiated"
    payout_settled = "payout_settled"
    rejected = "rejected"
    payout_failed = "payout_failed"


class Withdrawal(Base, TimestampMixin):
    __tablename__ = "withdrawals"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tds_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    payout_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    # Pocket breakdown: how much of `amount_paise` was sourced from each pocket.
    # Required so that on reject we can restore the original pocket composition.
    deposit_used_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    winnings_used_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    bank_account_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    ifsc: Mapped[str | None] = mapped_column(String(15), nullable=True)
    account_holder: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[WithdrawalStatus] = mapped_column(
        Enum(WithdrawalStatus, name="withdrawal_status"),
        default=WithdrawalStatus.requested,
        nullable=False,
        index=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    payout_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)


def to_rupees(paise: int) -> Decimal:
    return Decimal(paise) / Decimal(100)
