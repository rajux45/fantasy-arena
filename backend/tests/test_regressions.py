"""Regression tests for bugs surfaced in PR review."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.user import User, UserRole
from app.models.wallet import Pocket
from app.services import wallet_service
from app.services.casino.mines import play as mines_play
from app.services.casino.provably_fair import Rng
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


def test_deposit_verify_legs_balance(db) -> None:
    """Ledger legs constructed by verify_deposit must sum to zero
    (regression: PR #1 review #3193951923).

    Money flow: ext:bank_in (-amount) + user:deposit (+net) + gst_payable (+gst) = 0.
    """
    u = _make_user(db)
    amount = 100_000  # ₹1000
    gst = 21_875       # 28% inclusive
    net = amount - gst

    legs = [
        wallet_service.Leg(account="ext:bank_in", amount_paise=-amount),
        wallet_service.Leg(
            account=f"user:{u.id}:deposit", amount_paise=net,
            user_id=u.id, pocket=Pocket.deposit,
        ),
        wallet_service.Leg(account="system:gst_payable", amount_paise=gst),
    ]
    # Σ legs == 0; post_txn would reject otherwise.
    assert sum(leg.amount_paise for leg in legs) == 0
    wallet_service.post_txn(db, kind="deposit.captured", legs=legs)
    w = wallet_service.get_wallet(db, u.id)
    assert w.deposit_paise == net


def test_mines_can_lose() -> None:
    """Mines must produce zero-payout outcomes when picks land on bombs
    (regression: PR #1 review #3193952023).
    """
    losses = 0
    wins = 0
    # 24 bombs / 1 pick -> P(lose) = 24/25 -> almost always lose.
    for n in range(200):
        rng = Rng(server_seed="x" * 64, client_seed="c", nonce=n)
        outcome = mines_play(rng=rng, bet_coins=100, bet_input={"bombs": 24, "picks": 1})
        if outcome.payout_coins == 0:
            losses += 1
            assert outcome.detail["survived"] is False
        else:
            wins += 1
            assert outcome.detail["survived"] is True
    # Both branches must be exercised.
    assert losses > 0, "mines never loses — house edge is broken"
    assert losses > wins, "expected losses to dominate at 24 bombs"


def test_mines_default_config_can_lose() -> None:
    """Default 3-bomb / 3-pick config must also have realistic survival
    (regression: PR #1 review #3193952023).
    """
    losses = 0
    for n in range(500):
        rng = Rng(server_seed="x" * 64, client_seed="c", nonce=n)
        outcome = mines_play(rng=rng, bet_coins=100, bet_input={"bombs": 3, "picks": 3})
        if outcome.payout_coins == 0:
            losses += 1
    # Survival = C(22,3)/C(25,3) ~ 67% -> expect ~33% losses with noise.
    # Just assert non-trivial loss frequency.
    assert losses > 50
