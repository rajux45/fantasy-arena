"""Plinko (8/12/16 row, low/medium/high risk).

bet_input: { rows: 8|12|16, risk: "low"|"medium"|"high" }
"""
from __future__ import annotations

from app.services.casino.provably_fair import Rng

# Multiplier tables (symmetric). For brevity this is medium-risk approximations.
_MULTIPLIERS: dict[tuple[int, str], list[float]] = {
    (8, "low"): [5.6, 2.1, 1.1, 1.0, 0.5, 1.0, 1.1, 2.1, 5.6],
    (8, "medium"): [13, 3, 1.3, 0.7, 0.4, 0.7, 1.3, 3, 13],
    (8, "high"): [29, 4, 1.5, 0.3, 0.2, 0.3, 1.5, 4, 29],
    (12, "low"): [10, 3, 1.6, 1.4, 1.1, 1.0, 0.5, 1.0, 1.1, 1.4, 1.6, 3, 10],
    (12, "medium"): [33, 11, 4, 2, 1.1, 0.6, 0.3, 0.6, 1.1, 2, 4, 11, 33],
    (12, "high"): [170, 24, 8.1, 2, 0.7, 0.2, 0.2, 0.2, 0.7, 2, 8.1, 24, 170],
    (16, "low"): [16, 9, 2, 1.4, 1.4, 1.2, 1.1, 1.0, 0.5, 1.0, 1.1, 1.2, 1.4, 1.4, 2, 9, 16],
    (16, "medium"): [110, 41, 10, 5, 3, 1.5, 1, 0.5, 0.3, 0.5, 1, 1.5, 3, 5, 10, 41, 110],
    (16, "high"): [1000, 130, 26, 9, 4, 2, 0.2, 0.2, 0.2, 0.2, 0.2, 2, 4, 9, 26, 130, 1000],
}


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome

    rows = int(bet_input.get("rows", 12))
    risk = str(bet_input.get("risk", "medium"))
    multipliers = _MULTIPLIERS.get((rows, risk)) or _MULTIPLIERS[(12, "medium")]

    bucket = 0
    path: list[int] = []
    for _ in range(rows):
        bit = 1 if rng.uniform() < 0.5 else 0
        path.append(bit)
        bucket += bit
    multiplier = float(multipliers[bucket])
    payout = int(bet_coins * multiplier)
    return Outcome(multiplier=multiplier, payout_coins=payout, detail={"path": path, "bucket": bucket})
