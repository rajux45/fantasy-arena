"""Team validation per sport."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.player import Player, PlayerRole
from app.models.sport import SportSlug

CRICKET_TEAM_SIZE = 11
CRICKET_CREDIT_BUDGET = 100.0
CRICKET_ROLE_LIMITS = {
    PlayerRole.wicket_keeper: (1, 4),
    PlayerRole.batsman: (3, 6),
    PlayerRole.all_rounder: (1, 4),
    PlayerRole.bowler: (3, 6),
}

FOOTBALL_TEAM_SIZE = 11
FOOTBALL_CREDIT_BUDGET = 100.0
FOOTBALL_ROLE_LIMITS = {
    PlayerRole.goalkeeper: (1, 1),
    PlayerRole.defender: (3, 5),
    PlayerRole.midfielder: (3, 5),
    PlayerRole.forward: (1, 3),
}

KABADDI_TEAM_SIZE = 7
KABADDI_CREDIT_BUDGET = 100.0
KABADDI_ROLE_LIMITS = {
    PlayerRole.raider: (2, 4),
    PlayerRole.defender_kabaddi: (2, 4),
    PlayerRole.all_rounder_kabaddi: (1, 3),
}

BASKETBALL_TEAM_SIZE = 5
BASKETBALL_CREDIT_BUDGET = 100.0


@dataclass(frozen=True, slots=True)
class TeamValidation:
    ok: bool
    error: str | None = None
    total_credits: float = 0.0


def validate_team(
    db: Session,
    *,
    sport: SportSlug,
    player_ids: list[uuid.UUID],
    captain_id: uuid.UUID,
    vice_captain_id: uuid.UUID,
) -> TeamValidation:
    if captain_id == vice_captain_id:
        return TeamValidation(False, "captain and vice-captain must differ")
    if captain_id not in player_ids or vice_captain_id not in player_ids:
        return TeamValidation(False, "captain/vice-captain must be in selected players")

    if sport == SportSlug.cricket:
        size, budget, limits = CRICKET_TEAM_SIZE, CRICKET_CREDIT_BUDGET, CRICKET_ROLE_LIMITS
    elif sport == SportSlug.football:
        size, budget, limits = FOOTBALL_TEAM_SIZE, FOOTBALL_CREDIT_BUDGET, FOOTBALL_ROLE_LIMITS
    elif sport == SportSlug.kabaddi:
        size, budget, limits = KABADDI_TEAM_SIZE, KABADDI_CREDIT_BUDGET, KABADDI_ROLE_LIMITS
    elif sport == SportSlug.basketball:
        size, budget, limits = BASKETBALL_TEAM_SIZE, BASKETBALL_CREDIT_BUDGET, {}
    else:
        return TeamValidation(False, f"unsupported sport: {sport}")

    if len(player_ids) != size:
        return TeamValidation(False, f"team must have exactly {size} players")
    if len(set(player_ids)) != size:
        return TeamValidation(False, "duplicate players in team")

    players = db.query(Player).filter(Player.id.in_(player_ids)).all()
    if len(players) != size:
        return TeamValidation(False, "one or more players not found")

    total_credits = float(sum(float(p.credits) for p in players))
    if total_credits > budget + 0.001:
        return TeamValidation(False, f"team credits {total_credits} exceed budget {budget}")

    # max 7 players from any one team
    teamcounts: dict[str, int] = {}
    for p in players:
        teamcounts[p.team_name] = teamcounts.get(p.team_name, 0) + 1
        if teamcounts[p.team_name] > 7:
            return TeamValidation(False, "max 7 players from a single squad")

    if limits:
        rolecounts: dict[PlayerRole, int] = {}
        for p in players:
            rolecounts[p.role] = rolecounts.get(p.role, 0) + 1
        for role, (lo, hi) in limits.items():
            c = rolecounts.get(role, 0)
            if c < lo or c > hi:
                return TeamValidation(False, f"need {lo}-{hi} {role.value}, got {c}")

    return TeamValidation(True, None, total_credits)
