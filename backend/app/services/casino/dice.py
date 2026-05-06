"""Dice: target 0-100, choose over/under, win if roll satisfies prediction."""
from __future__ import annotations

from app.services.casino.provably_fair import Rng


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome

    target = float(bet_input.get("target", 50.5))
    direction = str(bet_input.get("direction", "over"))
    edge_bp = 200

    roll = round(rng.uniform() * 100, 4)

    if direction == "over":
        win_prob = max(0.0001, (100 - target) / 100)
        won = roll > target
    else:
        win_prob = max(0.0001, target / 100)
        won = roll < target

    fair_mult = 1.0 / win_prob
    multiplier = round(fair_mult * (1 - edge_bp / 10_000), 4) if won else 0.0
    payout = int(bet_coins * multiplier)
    return Outcome(multiplier=multiplier, payout_coins=payout, detail={"roll": roll})
