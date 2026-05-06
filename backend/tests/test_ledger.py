from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.user import User, UserRole
from app.models.wallet import Pocket
from app.services import wallet_service
from app.services.security import gen_referral_code


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    s = Session()
    try:
        yield s
    finally:
        s.close()


def _make_user(db) -> User:
    u = User(
        email=f"u-{uuid.uuid4().hex[:6]}@x.com",
        role=UserRole.user,
        referral_code=gen_referral_code(),
    )
    db.add(u)
    db.flush()
    return u


def test_balanced_post_passes(db) -> None:
    u = _make_user(db)
    txn = wallet_service.post_txn(
        db, kind="test.deposit",
        legs=[
            wallet_service.Leg(account=f"user:{u.id}:deposit", amount_paise=10_000,
                                user_id=u.id, pocket=Pocket.deposit),
            wallet_service.Leg(account="ext:bank_in", amount_paise=-10_000),
        ],
    )
    wallet_service.assert_ledger_balances(db, txn)
    w = wallet_service.get_wallet(db, u.id)
    assert w.deposit_paise == 10_000


def test_unbalanced_post_rejected(db) -> None:
    u = _make_user(db)
    with pytest.raises(wallet_service.LedgerError):
        wallet_service.post_txn(
            db, kind="bad",
            legs=[
                wallet_service.Leg(account=f"user:{u.id}:deposit", amount_paise=100,
                                   user_id=u.id, pocket=Pocket.deposit),
            ],
        )


def test_overspend_blocked(db) -> None:
    u = _make_user(db)
    with pytest.raises(wallet_service.LedgerError):
        wallet_service.post_txn(
            db, kind="bad.spend",
            legs=[
                wallet_service.Leg(account=f"user:{u.id}:deposit", amount_paise=-500,
                                   user_id=u.id, pocket=Pocket.deposit),
                wallet_service.Leg(account="system:burn", amount_paise=500),
            ],
        )


def test_casino_coins_isolated(db) -> None:
    u = _make_user(db)
    wallet_service.credit_casino_coins(db, user_id=u.id, coins=1000, kind="test.coin_credit")
    w = wallet_service.get_wallet(db, u.id)
    # Casino coins do NOT count as withdrawable
    assert wallet_service.withdrawable_paise(w) == 0
    assert w.casino_coins == 1000
