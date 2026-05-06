"""Simple 5x3 slot. Symbols + pay table based on a configured RTP (~96%)."""
from __future__ import annotations

from app.services.casino.provably_fair import Rng

SYMBOLS = ["7", "BAR", "BELL", "CHERRY", "LEMON", "PLUM"]
WEIGHTS = [1, 3, 6, 10, 14, 16]
PAYOUTS = {
    "7": {3: 50, 4: 200, 5: 1000},
    "BAR": {3: 20, 4: 80, 5: 400},
    "BELL": {3: 8, 4: 25, 5: 100},
    "CHERRY": {3: 4, 4: 12, 5: 40},
    "LEMON": {3: 3, 4: 8, 5: 25},
    "PLUM": {3: 2, 4: 6, 5: 18},
}


def _weighted(rng: Rng) -> str:
    total = sum(WEIGHTS)
    pick = rng.randint(0, total - 1)
    acc = 0
    for sym, w in zip(SYMBOLS, WEIGHTS, strict=False):
        acc += w
        if pick < acc:
            return sym
    return SYMBOLS[-1]


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome

    reels = [[_weighted(rng) for _ in range(3)] for _ in range(5)]

    # 5 paylines (each row + 2 v-shapes); we evaluate left-to-right from reel 0.
    lines = [
        [reels[r][0] for r in range(5)],  # top row
        [reels[r][1] for r in range(5)],  # middle row
        [reels[r][2] for r in range(5)],  # bottom row
    ]

    multiplier = 0.0
    wins: list[dict] = []
    for line in lines:
        first = line[0]
        run = 1
        for s in line[1:]:
            if s == first:
                run += 1
            else:
                break
        if run >= 3:
            mult = PAYOUTS[first].get(run, 0)
            multiplier += mult
            wins.append({"symbol": first, "run": run, "multiplier": mult})

    payout = int(bet_coins * multiplier)
    return Outcome(multiplier=multiplier, payout_coins=payout, detail={"reels": reels, "wins": wins})
