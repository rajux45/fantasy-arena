"""Kabaddi fantasy scoring (PKL-style).

Stats schema:
    raid_points, touch_points, bonus_points, super_raids,
    tackle_points, super_tackles, all_out_points (team), high_5 (bool),
    super_10 (bool), played (bool), role,
    is_captain, is_vice_captain, is_mvp,
"""
from __future__ import annotations


def compute_points(stats: dict) -> float:
    if not stats.get("played", False):
        return 0.0

    pts = 4.0
    pts += float(stats.get("raid_points", 0)) * 1
    pts += float(stats.get("touch_points", 0)) * 1
    pts += float(stats.get("bonus_points", 0)) * 1
    pts += float(stats.get("super_raids", 0)) * 4
    pts += float(stats.get("tackle_points", 0)) * 2
    pts += float(stats.get("super_tackles", 0)) * 4
    pts += float(stats.get("all_out_points", 0)) * 2

    if stats.get("super_10"):  # 10+ raid points
        pts += 6
    if stats.get("high_5"):   # 5+ tackle points
        pts += 6

    if stats.get("is_mvp"):
        pts += 6

    if stats.get("is_captain"):
        pts *= 2.0
    elif stats.get("is_vice_captain"):
        pts *= 1.5

    return pts
