"""Football fantasy scoring.

Stats schema:
    minutes_played, goals, assists, clean_sheet (bool), goals_conceded,
    saves, shots_on_target, key_passes, tackles, pass_accuracy_pct,
    yellow_cards, red_cards,
    penalty_saved, penalty_missed, own_goal,
    role: GK | DEF | MID | FWD,
    played (bool), is_captain, is_vice_captain, is_motm,
"""
from __future__ import annotations

GOAL_PTS = {"GK": 12, "DEF": 10, "MID": 8, "FWD": 6}
ASSIST_PTS = 6


def compute_points(stats: dict) -> float:
    if not stats.get("played", False):
        return 0.0

    role = str(stats.get("role", "MID")).upper()
    minutes = int(stats.get("minutes_played", 0))

    pts = 0.0
    pts += 2.0 if minutes >= 60 else (1.0 if minutes >= 1 else 0.0)
    pts += float(stats.get("goals", 0)) * GOAL_PTS.get(role, 6)
    pts += float(stats.get("assists", 0)) * ASSIST_PTS
    pts += float(stats.get("shots_on_target", 0)) * 0.5
    pts += float(stats.get("key_passes", 0)) * 0.4
    pts += float(stats.get("tackles", 0)) * 0.4

    pa = float(stats.get("pass_accuracy_pct", 0))
    if pa >= 85: pts += 2
    elif pa >= 70: pts += 1

    if role in {"GK", "DEF"} and stats.get("clean_sheet"):
        pts += 4
    if role == "MID" and stats.get("clean_sheet"):
        pts += 1

    saves = int(stats.get("saves", 0))
    if role == "GK":
        pts += (saves // 3) * 3
    if stats.get("penalty_saved"):
        pts += 8
    if stats.get("penalty_missed"):
        pts -= 4

    conceded = int(stats.get("goals_conceded", 0))
    if role in {"GK", "DEF"}:
        pts -= (conceded // 2) * 1

    pts -= float(stats.get("yellow_cards", 0)) * 1
    pts -= float(stats.get("red_cards", 0)) * 3
    pts -= float(stats.get("own_goal", 0)) * 4

    if stats.get("is_motm"):
        pts += 6

    if stats.get("is_captain"):
        pts *= 2.0
    elif stats.get("is_vice_captain"):
        pts *= 1.5

    return pts
