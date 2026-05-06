"""Casino round orchestration: seed mgmt + bet/payout in coins (no rupees)."""
from __future__ import annotations

import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.casino import CasinoGameSlug, CasinoRound, CasinoSeed
from app.services import wallet_service
from app.services.casino import Seeds, play
from app.services.casino.provably_fair import commit


class CasinoError(Exception):
    pass


def get_or_create_seed(db: Session, user_id: uuid.UUID, client_seed: str | None = None) -> CasinoSeed:
    seed = db.execute(
        select(CasinoSeed).where(CasinoSeed.user_id == user_id, CasinoSeed.is_revealed == False)  # noqa: E712
    ).scalar_one_or_none()
    if seed:
        if client_seed:
            seed.client_seed = client_seed
            db.flush()
        return seed
    server_seed = secrets.token_hex(32)
    new = CasinoSeed(
        user_id=user_id,
        server_seed=server_seed,
        server_seed_hash=commit(server_seed),
        client_seed=client_seed or secrets.token_hex(8),
        nonce=0,
        is_revealed=False,
    )
    db.add(new)
    db.flush()
    return new


def rotate_seed(db: Session, user_id: uuid.UUID) -> CasinoSeed:
    """Reveal previous server_seed and issue a new one."""
    old = db.execute(
        select(CasinoSeed).where(CasinoSeed.user_id == user_id, CasinoSeed.is_revealed == False)  # noqa: E712
    ).scalar_one_or_none()
    if old:
        old.is_revealed = True
    new_server = secrets.token_hex(32)
    new = CasinoSeed(
        user_id=user_id,
        server_seed=new_server,
        server_seed_hash=commit(new_server),
        client_seed=secrets.token_hex(8),
        nonce=0,
        is_revealed=False,
    )
    db.add(new)
    db.flush()
    return new


def play_round(
    db: Session,
    *,
    user_id: uuid.UUID,
    game: CasinoGameSlug,
    bet_coins: int,
    bet_input: dict,
) -> CasinoRound:
    if bet_coins <= 0:
        raise CasinoError("bet must be positive")

    seed = get_or_create_seed(db, user_id)
    if seed.server_seed is None:
        raise CasinoError("seed not initialized")

    wallet = wallet_service.get_wallet(db, user_id)
    if wallet.casino_coins < bet_coins:
        raise CasinoError("insufficient casino coins")

    # 1) debit
    wallet_service.debit_casino_coins(
        db, user_id=user_id, coins=bet_coins, kind="casino.bet",
        meta={"game": game.value, "nonce": seed.nonce},
    )

    # 2) play
    outcome = play(
        slug=game,
        seeds=Seeds(server_seed=seed.server_seed, client_seed=seed.client_seed, nonce=seed.nonce),
        bet_coins=bet_coins,
        bet_input=bet_input,
    )

    # 3) credit payout
    if outcome.payout_coins > 0:
        wallet_service.credit_casino_coins(
            db, user_id=user_id, coins=outcome.payout_coins, kind="casino.payout",
            meta={"game": game.value, "nonce": seed.nonce, "multiplier": outcome.multiplier},
        )

    # 4) record
    rnd = CasinoRound(
        user_id=user_id,
        game_slug=game,
        bet_coins=bet_coins,
        payout_coins=outcome.payout_coins,
        multiplier=outcome.multiplier,
        server_seed_hash=seed.server_seed_hash,
        server_seed=None,  # revealed only on rotation
        client_seed=seed.client_seed,
        nonce=seed.nonce,
        outcome=outcome.detail,
        bet_input=bet_input,
    )
    db.add(rnd)
    seed.nonce = seed.nonce + 1
    db.flush()
    return rnd
