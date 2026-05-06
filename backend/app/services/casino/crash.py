"""Crash multiplier game.

bet_input: { "auto_cashout": float (e.g. 1.50) }
"""
from __future__ import annotations

import math

from app.services.casino.provably_fair import Rng


def crash_point(rng: Rng, house_edge_bp: int = 200) -> float:
    """Compute crash multiplier from one uniform sample. House edge applied via floor.

    M = 0.99 / (1 - U), capped at 1.00 from below; with house edge converting some to instant 1.00 bust.
    """
    u = rng.uniform()
    edge = house_edge_bp / 10_000.0  # 200 bp -> 2%
    if u < edge:
        return 1.00
    # Map u' from [edge, 1) -> [0, 1)
    up = (u - edge) / (1.0 - edge)
    if up >= 0.99999999:
        up = 0.99999999
    m = 1.0 / (1.0 - up)
    return math.floor(m * 100) / 100.0


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome  # avoid circular

    auto_cashout = float(bet_input.get("auto_cashout", 0))
    crash = crash_point(rng)
    if auto_cashout > 1.0 and crash >= auto_cashout:
        multiplier = auto_cashout
        payout = int(bet_coins * multiplier)
    else:
        multiplier = 0.0
        payout = 0
    return Outcome(multiplier=multiplier, payout_coins=payout, detail={"crash": crash})
