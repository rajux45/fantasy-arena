from __future__ import annotations

from app.models.sport import SportSlug
from app.services.scoring import compute_points


def test_cricket_zero_when_did_not_play() -> None:
    assert compute_points(SportSlug.cricket, {"played": False, "match_format": "T20"}) == 0


def test_cricket_balanced_score() -> None:
    pts = compute_points(SportSlug.cricket, {
        "played": True, "match_format": "T20",
        "runs": 50, "balls_faced": 30, "fours": 5, "sixes": 2,
        "wickets": 2, "balls_bowled": 24, "runs_conceded": 28,
        "catches": 1,
    })
    # 4 (lineup) + 50 + 5 + 4 + 8 (50-bonus) + SR≈166 -> +4
    # + 2*25 (wickets) + econ 7 -> 0 + 1 catch * 8 = ~133
    assert pts > 100


def test_cricket_captain_doubles() -> None:
    base = compute_points(SportSlug.cricket, {
        "played": True, "match_format": "T20", "runs": 30, "balls_faced": 20,
    })
    cap = compute_points(SportSlug.cricket, {
        "played": True, "match_format": "T20", "runs": 30, "balls_faced": 20,
        "is_captain": True,
    })
    assert abs(cap - 2 * base) < 0.01


def test_football_goal_value_by_role() -> None:
    pts_gk = compute_points(SportSlug.football, {
        "played": True, "minutes_played": 90, "role": "GK", "goals": 1,
    })
    pts_fwd = compute_points(SportSlug.football, {
        "played": True, "minutes_played": 90, "role": "FWD", "goals": 1,
    })
    assert pts_gk > pts_fwd


def test_kabaddi_super_10() -> None:
    pts = compute_points(SportSlug.kabaddi, {
        "played": True, "raid_points": 10, "super_10": True,
    })
    # 4 + 10 + 6 = 20
    assert pts == 20.0


def test_basketball_double_double() -> None:
    pts = compute_points(SportSlug.basketball, {
        "played": True, "points": 22, "rebounds": 11, "assists": 6,
        "double_double": True,
    })
    # 22*1 + 11*1.2 + 6*1.5 + 6 (DD bonus) = 50.2
    assert abs(pts - 50.2) < 0.01
