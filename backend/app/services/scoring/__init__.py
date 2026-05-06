"""Per-sport fantasy scoring engines."""
from __future__ import annotations

from collections.abc import Callable

from app.models.sport import SportSlug
from app.services.scoring import basketball, cricket, football, kabaddi

ENGINES: dict[SportSlug, Callable[[dict], float]] = {
    SportSlug.cricket: cricket.compute_points,
    SportSlug.football: football.compute_points,
    SportSlug.kabaddi: kabaddi.compute_points,
    SportSlug.basketball: basketball.compute_points,
}


def compute_points(sport: SportSlug, stats: dict) -> float:
    fn = ENGINES.get(sport)
    if fn is None:
        raise ValueError(f"no scoring engine for sport {sport}")
    return round(fn(stats), 2)
