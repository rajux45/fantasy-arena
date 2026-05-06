"""European roulette (single zero). Bets on color, even/odd, dozens, single number."""
from __future__ import annotations

from app.services.casino.provably_fair import Rng

REDS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


def _payout_multiplier(bet_type: str, value, number: int) -> float:
    if bet_type == "red":
        return 2.0 if number in REDS and number != 0 else 0.0
    if bet_type == "black":
        return 2.0 if (number not in REDS) and number != 0 else 0.0
    if bet_type == "even":
        return 2.0 if number != 0 and number % 2 == 0 else 0.0
    if bet_type == "odd":
        return 2.0 if number != 0 and number % 2 == 1 else 0.0
    if bet_type == "low":
        return 2.0 if 1 <= number <= 18 else 0.0
    if bet_type == "high":
        return 2.0 if 19 <= number <= 36 else 0.0
    if bet_type == "dozen":
        d = int(value)
        if d == 1 and 1 <= number <= 12: return 3.0
        if d == 2 and 13 <= number <= 24: return 3.0
        if d == 3 and 25 <= number <= 36: return 3.0
        return 0.0
    if bet_type == "straight":
        return 36.0 if int(value) == number else 0.0
    return 0.0


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome

    number = rng.randint(0, 36)
    bet_type = str(bet_input.get("bet_type", "red"))
    value = bet_input.get("value")

    multiplier = _payout_multiplier(bet_type, value, number)
    payout = int(bet_coins * multiplier)
    return Outcome(multiplier=multiplier, payout_coins=payout, detail={"number": number})
