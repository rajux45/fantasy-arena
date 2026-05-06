from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.casino import CasinoGameSlug, CasinoRound
from app.models.user import User
from app.schemas.casino import BetIn, CoinPackagePurchase, RoundOut, SeedInfo, SeedRotateOut
from app.services import casino_service, wallet_service

router = APIRouter(prefix="/v1/casino", tags=["casino"])


COIN_PACKAGES = {
    "starter": {"price_paise": 5000, "coins": 5_000},
    "bronze": {"price_paise": 10000, "coins": 11_000},
    "silver": {"price_paise": 50000, "coins": 60_000},
    "gold": {"price_paise": 100000, "coins": 130_000},
    "platinum": {"price_paise": 500000, "coins": 700_000},
}


@router.get("/packages")
def coin_packages():
    return [{"slug": k, **v} for k, v in COIN_PACKAGES.items()]


@router.post("/coins/purchase")
def purchase_package(
    payload: CoinPackagePurchase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """In production this would create a Razorpay order; for MVP we credit immediately if the user has enough deposit balance."""
    pkg = COIN_PACKAGES.get(payload.package_slug)
    if pkg is None:
        raise HTTPException(404, "unknown package")
    w = wallet_service.get_wallet(db, user.id)
    if w.deposit_paise < pkg["price_paise"]:
        raise HTTPException(400, "insufficient deposit balance — top up first")

    # Debit deposit, credit casino coins (one-way; no path back to fiat).
    wallet_service.post_txn(
        db,
        kind="casino.coins_purchase",
        legs=[
            wallet_service.Leg(
                account=f"user:{user.id}:deposit", amount_paise=-pkg["price_paise"],
                user_id=user.id,
                pocket=__import__("app.models.wallet", fromlist=["Pocket"]).Pocket.deposit,
            ),
            wallet_service.Leg(
                account="system:casino_revenue", amount_paise=pkg["price_paise"],
                meta={"package": payload.package_slug},
            ),
        ],
    )
    wallet_service.credit_casino_coins(
        db, user_id=user.id, coins=pkg["coins"], kind="casino.coins_credit",
        meta={"package": payload.package_slug},
    )
    db.commit()
    return {"coins_credited": pkg["coins"]}


@router.get("/seed", response_model=SeedInfo)
def my_seed(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = casino_service.get_or_create_seed(db, user.id)
    db.commit()
    return SeedInfo(server_seed_hash=s.server_seed_hash, client_seed=s.client_seed, nonce=s.nonce)


@router.post("/seed/rotate", response_model=SeedRotateOut)
def rotate_seed(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # We need the prior seed's value before rotation.
    prev = db.execute(
        select(__import__("app.models.casino", fromlist=["CasinoSeed"]).CasinoSeed)
        .where(
            __import__("app.models.casino", fromlist=["CasinoSeed"]).CasinoSeed.user_id == user.id,
            __import__("app.models.casino", fromlist=["CasinoSeed"]).CasinoSeed.is_revealed == False,  # noqa: E712
        )
    ).scalar_one_or_none()
    revealed = prev.server_seed if prev else None
    new = casino_service.rotate_seed(db, user.id)
    db.commit()
    return SeedRotateOut(
        revealed_server_seed=revealed,
        new_server_seed_hash=new.server_seed_hash,
        new_client_seed=new.client_seed,
    )


@router.post("/play", response_model=RoundOut)
def play(
    payload: BetIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        slug = CasinoGameSlug(payload.game)
    except ValueError as exc:
        raise HTTPException(400, "unknown game") from exc

    try:
        rnd = casino_service.play_round(
            db, user_id=user.id, game=slug,
            bet_coins=payload.bet_coins, bet_input=payload.bet_input,
        )
    except casino_service.CasinoError as exc:
        raise HTTPException(400, str(exc)) from exc
    db.commit()
    return _round_to_out(rnd)


@router.get("/rounds", response_model=list[RoundOut])
def my_rounds(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(CasinoRound)
        .where(CasinoRound.user_id == user.id)
        .order_by(desc(CasinoRound.created_at))
        .limit(min(limit, 200))
    ).scalars().all()
    return [_round_to_out(r) for r in rows]


def _round_to_out(r: CasinoRound) -> RoundOut:
    return RoundOut(
        id=str(r.id),
        game=r.game_slug.value,
        bet_coins=r.bet_coins,
        payout_coins=r.payout_coins,
        multiplier=float(r.multiplier or 0),
        server_seed_hash=r.server_seed_hash,
        server_seed=r.server_seed,
        client_seed=r.client_seed,
        nonce=r.nonce,
        outcome=r.outcome,
        bet_input=r.bet_input,
    )
