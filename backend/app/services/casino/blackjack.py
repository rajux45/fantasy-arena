"""Single-hand auto-played blackjack vs dealer. Single deck.

Strategy is deterministic basic strategy (server-side) so RNG is the only stochastic input.
bet_input: optional { "auto": true } — currently the only mode.
"""
from __future__ import annotations

from app.services.casino.provably_fair import Rng

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["S", "H", "D", "C"]


def _shuffled_deck(rng: Rng) -> list[str]:
    deck = [f"{r}{s}" for s in SUITS for r in RANKS]
    # Fisher-Yates with provable RNG
    for i in range(len(deck) - 1, 0, -1):
        j = rng.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]
    return deck


def _hand_value(hand: list[str]) -> int:
    total = 0
    aces = 0
    for c in hand:
        r = c[:-1]
        if r == "A":
            total += 11
            aces += 1
        elif r in {"K", "Q", "J", "10"}:
            total += 10
        else:
            total += int(r)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def play(*, rng: Rng, bet_coins: int, bet_input: dict):
    from app.services.casino import Outcome

    deck = _shuffled_deck(rng)
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    # Player auto-strategy: hit until 17 (soft 17 hits)
    while _hand_value(player) < 17:
        player.append(deck.pop())

    # Dealer plays after; hits soft 17 to give house slight edge
    while _hand_value(dealer) < 17:
        dealer.append(deck.pop())

    p, d = _hand_value(player), _hand_value(dealer)
    player_blackjack = (len(player) == 2 and p == 21)
    dealer_blackjack = (len(dealer) == 2 and d == 21)

    if p > 21:
        multiplier = 0.0
    elif dealer_blackjack and not player_blackjack:
        # Dealer's natural 21 beats a non-natural player 21 (and any other
        # player hand that isn't itself a natural). Without this, the `p == d`
        # branch below would pay out a push when both totals were 21.
        multiplier = 0.0
    elif d > 21 or p > d:
        multiplier = 2.5 if player_blackjack else 2.0
    elif p == d:
        multiplier = 1.0  # push
    else:
        multiplier = 0.0

    payout = int(bet_coins * multiplier)
    return Outcome(
        multiplier=multiplier,
        payout_coins=payout,
        detail={
            "player": player,
            "dealer": dealer,
            "p": p,
            "d": d,
            "player_blackjack": player_blackjack,
            "dealer_blackjack": dealer_blackjack,
        },
    )
