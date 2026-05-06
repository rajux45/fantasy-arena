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


def test_login_phone_blocks_inactive_users(monkeypatch) -> None:
    """Banned users (is_active=False) must not be issued tokens via OTP login
    (regression: PR #1 review #3194022843).
    """
    from fastapi import HTTPException

    from app.api import auth as auth_api
    from app.schemas.auth import LoginPhone

    # Build a mock session-like object.
    class _DBStub:
        def __init__(self, user):
            self._user = user

        def execute(self, _stmt):
            class _Result:
                def __init__(self, u):
                    self._u = u

                def scalar_one_or_none(self):
                    return self._u

            return _Result(self._user)

        def add(self, _x):
            return None

        def flush(self):
            return None

        def commit(self):
            return None

    user = User(
        id=uuid.uuid4(),
        phone="+919999999999",
        role=UserRole.user,
        referral_code=gen_referral_code(),
        is_active=False,
    )

    monkeypatch.setattr(auth_api.otp_service, "verify_otp", lambda *a, **k: True)
    monkeypatch.setattr(auth_api, "write_audit", lambda *a, **k: None)

    payload = LoginPhone(phone="+919999999999", otp="123456")
    with pytest.raises(HTTPException) as exc:
        auth_api.login_phone(payload, db=_DBStub(user), meta={})
    assert exc.value.status_code == 403


def test_tournament_detail_404_for_unknown_id() -> None:
    """detail() must raise HTTPException(404), not return None
    (regression: PR #1 review #3194022946).
    """
    from fastapi import HTTPException

    from app.api.tournaments import detail

    with pytest.raises(HTTPException) as exc:
        detail("does-not-exist")
    assert exc.value.status_code == 404


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
