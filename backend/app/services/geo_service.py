"""Geo-fencing for state-wise restrictions on real-money fantasy contests."""
from __future__ import annotations

# Indian state codes where pay-to-play fantasy is restricted (update per latest legal opinion).
RESTRICTED_FANTASY_STATES: frozenset[str] = frozenset(
    {"AS", "OD", "NL", "SK", "TG", "AP"}
)

ALL_INDIA_STATE_CODES: frozenset[str] = frozenset(
    {
        "AN", "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "DN", "GA", "GJ", "HP",
        "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH", "ML", "MN", "MP", "MZ", "NL",
        "OD", "PB", "PY", "RJ", "SK", "TG", "TN", "TR", "UK", "UP", "WB",
    }
)


def is_fantasy_real_money_allowed(state_code: str | None) -> bool:
    if not state_code:
        # Without a confirmed state we conservatively allow (KYC will collect state).
        # Tighten in production by requiring state before any paid action.
        return True
    return state_code.upper() not in RESTRICTED_FANTASY_STATES


def is_state_supported(state_code: str | None) -> bool:
    if not state_code:
        return False
    return state_code.upper() in ALL_INDIA_STATE_CODES
