"""Cricket fantasy scoring (Dream11 T20-style by default).

Stats schema (all optional ints / floats unless noted):
    runs, balls_faced, fours, sixes,
    overs, balls_bowled, runs_conceded, wickets, maidens,
    catches, stumpings, run_outs_direct, run_outs_indirect,
    duck (bool), played (bool), match_format ("T20" | "ODI" | "Test"),
    is_captain (bool), is_vice_captain (bool),
    is_pom (bool, player-of-the-match),
    impact_player (bool),
"""
from __future__ import annotations


def _batting_points(s: dict, fmt: str) -> float:
    pts = 0.0
    runs = float(s.get("runs", 0))
    boundaries = float(s.get("fours", 0))
    sixes = float(s.get("sixes", 0))
    balls = float(s.get("balls_faced", 0))

    pts += runs                     # 1 pt per run
    pts += boundaries * 1           # +1 per four
    pts += sixes * 2                # +2 per six

    # Milestone bonuses (T20 thresholds; ODI shifted upward, Test minimal)
    if fmt == "T20":
        if runs >= 100: pts += 16
        elif runs >= 50: pts += 8
        elif runs >= 30: pts += 4
    elif fmt == "ODI":
        if runs >= 100: pts += 8
        elif runs >= 50: pts += 4
    elif fmt == "Test":
        if runs >= 100: pts += 8
        elif runs >= 50: pts += 4

    # Strike rate (T20 only, for batsmen who faced ≥10 balls)
    if fmt == "T20" and balls >= 10 and runs > 0:
        sr = runs * 100.0 / balls
        if sr >= 170: pts += 6
        elif sr >= 150: pts += 4
        elif sr >= 130: pts += 2
        elif sr < 50: pts -= 6
        elif sr < 60: pts -= 4
        elif sr < 70: pts -= 2

    # Duck (T20/ODI batsman/wk/all-rounder dismissed for 0)
    if s.get("duck") and fmt != "Test":
        pts -= 2

    return pts


def _bowling_points(s: dict, fmt: str) -> float:
    pts = 0.0
    wickets = float(s.get("wickets", 0))
    pts += wickets * 25
    if wickets >= 5: pts += 16
    elif wickets >= 4: pts += 8
    elif wickets >= 3: pts += 4

    # LBW / bowled bonus (count as separate stat)
    pts += float(s.get("bowled_or_lbw", 0)) * 8

    pts += float(s.get("maidens", 0)) * 12

    balls = float(s.get("balls_bowled", 0))
    runs = float(s.get("runs_conceded", 0))
    if fmt == "T20" and balls >= 12:
        econ = runs * 6.0 / balls
        if econ < 5: pts += 6
        elif econ < 6: pts += 4
        elif econ < 7: pts += 2
        elif econ > 12: pts -= 6
        elif econ > 11: pts -= 4
        elif econ > 10: pts -= 2

    return pts


def _fielding_points(s: dict) -> float:
    pts = 0.0
    catches = int(s.get("catches", 0))
    pts += catches * 8
    if catches >= 3: pts += 4  # 3-catch bonus
    pts += int(s.get("stumpings", 0)) * 12
    pts += int(s.get("run_outs_direct", 0)) * 12
    pts += int(s.get("run_outs_indirect", 0)) * 6
    return pts


def compute_points(stats: dict) -> float:
    if not stats.get("played", False):
        return 0.0

    fmt = str(stats.get("match_format", "T20")).upper()
    if fmt not in {"T20", "ODI", "TEST"}:
        fmt = "T20"
    fmt_norm = "T20" if fmt == "T20" else ("ODI" if fmt == "ODI" else "Test")

    pts = 4.0  # turning-up / lineup credit
    pts += _batting_points(stats, fmt_norm)
    pts += _bowling_points(stats, fmt_norm)
    pts += _fielding_points(stats)

    if stats.get("is_pom"):
        pts += 6

    if stats.get("impact_player"):
        pts *= 1.0  # already applied through stats; no further multiplier here

    if stats.get("is_captain"):
        pts *= 2.0
    elif stats.get("is_vice_captain"):
        pts *= 1.5

    return pts
