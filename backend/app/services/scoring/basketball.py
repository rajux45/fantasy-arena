"""Basketball fantasy scoring (NBA / Indian Basketball League).

Stats schema:
    points, threes, free_throws_made,
    rebounds, assists, steals, blocks,
    turnovers, fouls, played (bool), minutes_played,
    is_captain, is_vice_captain, double_double (bool), triple_double (bool),
"""
from __future__ import annotations


def compute_points(stats: dict) -> float:
    if not stats.get("played", False):
        return 0.0

    pts = 0.0
    pts += float(stats.get("points", 0)) * 1
    pts += float(stats.get("threes", 0)) * 1
    pts += float(stats.get("free_throws_made", 0)) * 0.5
    pts += float(stats.get("rebounds", 0)) * 1.2
    pts += float(stats.get("assists", 0)) * 1.5
    pts += float(stats.get("steals", 0)) * 2
    pts += float(stats.get("blocks", 0)) * 2
    pts -= float(stats.get("turnovers", 0)) * 1
    pts -= float(stats.get("fouls", 0)) * 0.5

    if stats.get("triple_double"):
        pts += 12
    elif stats.get("double_double"):
        pts += 6

    if stats.get("is_captain"):
        pts *= 2.0
    elif stats.get("is_vice_captain"):
        pts *= 1.5

    return pts
