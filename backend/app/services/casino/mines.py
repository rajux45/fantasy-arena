"""Mines: 5x5 grid; user picks N safe tiles; payout grows with picks."""
from __future__ import annotations

from app.services.casino.provably_fair import Rng

GRID = 25  # 5x5


def _bomb_positions(rng: Rng, n_bombs: int) -> list[int]:
    pool = list(range(GRID))
    bombs: list[int] = []
    for _ in range(n_bombs):
        idx = rng.randint(0, len(pool) - 1)
        bombs.append(pool.pop(idx))
    return sorted(bombs)


def _multiplier(bombs: int, picks: int, edge_bp: int = 200) -> float:
    """Fair payout = C(25, picks) / C(25 - bombs, picks); subtract edge."""
    if picks == 0:
        return 1.0
    safe = GRID - bombs
    num = 1.0
    den = 1.0
    for k in range(picks):
        num *= (GRID - k)
        den *= (safe - k)
    fair = num / den
    edge = edge_bp / 10_000.0
    return round(fair * (1 - edge), 4)


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    """Auto-resolve: server places bombs, then picks `picks_count` random tiles
    from the *full* grid. If any pick lands on a bomb, the player loses (payout 0).
    Otherwise the player wins `multiplier * bet`.

    Survival probability is C(25-bombs, picks) / C(25, picks); the multiplier on
    survival is its inverse minus a small house edge, so EV is approximately
    (1 - edge) * bet.
    """
    from app.services.casino import Outcome

    bombs = max(1, min(int(bet_input.get("bombs", 3)), 24))
    picks_count = max(1, min(int(bet_input.get("picks", 3)), GRID - bombs))

    bomb_positions = _bomb_positions(rng, bombs)
    bomb_set = set(bomb_positions)

    pool = list(range(GRID))
    picks: list[int] = []
    survived = True
    for _ in range(picks_count):
        idx = rng.randint(0, len(pool) - 1)
        tile = pool.pop(idx)
        picks.append(tile)
        if tile in bomb_set:
            survived = False
            break

    if not survived:
        multiplier, payout = 0.0, 0
    else:
        multiplier = _multiplier(bombs, picks_count)
        payout = int(bet_coins * multiplier)

    return Outcome(
        multiplier=multiplier,
        payout_coins=payout,
        detail={"bombs": bomb_positions, "picks": picks, "survived": survived},
    )
