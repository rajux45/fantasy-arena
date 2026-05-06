from __future__ import annotations

from app.services.geo_service import (
    RESTRICTED_FANTASY_STATES,
    is_fantasy_real_money_allowed,
    is_state_supported,
)


def test_restricted_states_blocked() -> None:
    for st in RESTRICTED_FANTASY_STATES:
        assert not is_fantasy_real_money_allowed(st)


def test_other_states_allowed() -> None:
    assert is_fantasy_real_money_allowed("MH")
    assert is_fantasy_real_money_allowed("KA")


def test_unknown_state_is_allowed_but_unsupported() -> None:
    assert is_fantasy_real_money_allowed(None)  # conservative allow
    assert not is_state_supported("XX")
    assert is_state_supported("MH")
