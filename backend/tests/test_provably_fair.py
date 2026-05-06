from __future__ import annotations

from app.models.casino import CasinoGameSlug
from app.services.casino import Seeds, play
from app.services.casino.provably_fair import Rng, commit


def test_rng_is_deterministic() -> None:
    a = Rng("server", "client", 0)
    b = Rng("server", "client", 0)
    seq_a = [a.uniform() for _ in range(10)]
    seq_b = [b.uniform() for _ in range(10)]
    assert seq_a == seq_b


def test_commit_independent_of_inputs() -> None:
    h = commit("server-seed-1")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_crash_returns_at_least_1() -> None:
    out = play(CasinoGameSlug.crash, Seeds("ss", "cs", 1), bet_coins=100, bet_input={"auto_cashout": 1.5})
    assert "crash" in out.detail
    assert out.detail["crash"] >= 1.0


def test_dice_over_under_consistency() -> None:
    out_over = play(CasinoGameSlug.dice, Seeds("seed-x", "client-x", 0), 100, {"target": 50.5, "direction": "over"})
    out_under = play(CasinoGameSlug.dice, Seeds("seed-x", "client-x", 0), 100, {"target": 50.5, "direction": "under"})
    # Same RNG, same roll — exactly one of (over, under) wins.
    assert (out_over.payout_coins > 0) ^ (out_under.payout_coins > 0)


def test_roulette_returns_valid_number() -> None:
    out = play(CasinoGameSlug.roulette, Seeds("a", "b", 0), 100, {"bet_type": "red"})
    assert 0 <= out.detail["number"] <= 36


def test_blackjack_round_executes() -> None:
    out = play(CasinoGameSlug.blackjack, Seeds("a", "b", 0), 100, {})
    assert "player" in out.detail
    assert "dealer" in out.detail
