"""Casino games — play-money only. Each game module exports `play(seeds, bet_input) -> Outcome`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.casino import CasinoGameSlug
from app.services.casino import (
    blackjack,
    crash,
    dice,
    mines,
    plinko,
    provably_fair,
    roulette,
    slots,
)


@dataclass(frozen=True, slots=True)
class Seeds:
    server_seed: str
    client_seed: str
    nonce: int


@dataclass(frozen=True, slots=True)
class Outcome:
    multiplier: float
    payout_coins: int
    detail: dict[str, Any]


GAMES = {
    CasinoGameSlug.crash: crash,
    CasinoGameSlug.plinko: plinko,
    CasinoGameSlug.mines: mines,
    CasinoGameSlug.dice: dice,
    CasinoGameSlug.roulette: roulette,
    CasinoGameSlug.slots: slots,
    CasinoGameSlug.blackjack: blackjack,
}


def play(slug: CasinoGameSlug, seeds: Seeds, bet_coins: int, bet_input: dict[str, Any]) -> Outcome:
    mod = GAMES[slug]
    rng = provably_fair.Rng(seeds.server_seed, seeds.client_seed, seeds.nonce)
    return mod.play(rng=rng, bet_coins=bet_coins, bet_input=bet_input)
