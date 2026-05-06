from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.player import Player, PlayerRole
from app.models.sport import Sport, SportSlug
from app.services.team_service import validate_team


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False, future=True)
    s = Session()
    try:
        yield s
    finally:
        s.close()


def _seed_cricket(db):
    sport = Sport(slug=SportSlug.cricket, name="Cricket", is_active=True)
    db.add(sport)
    db.flush()
    roster = [
        # 1 wk, 4 bat, 2 ar, 4 bowl from two teams
        ("WK1", "A", PlayerRole.wicket_keeper, 9.0),
        ("BAT1", "A", PlayerRole.batsman, 9.0),
        ("BAT2", "A", PlayerRole.batsman, 9.0),
        ("BAT3", "B", PlayerRole.batsman, 9.0),
        ("BAT4", "B", PlayerRole.batsman, 9.0),
        ("AR1", "A", PlayerRole.all_rounder, 9.0),
        ("AR2", "B", PlayerRole.all_rounder, 9.0),
        ("BOWL1", "A", PlayerRole.bowler, 9.0),
        ("BOWL2", "B", PlayerRole.bowler, 9.0),
        ("BOWL3", "B", PlayerRole.bowler, 9.0),
        ("BOWL4", "A", PlayerRole.bowler, 9.0),
    ]
    players = []
    for name, team, role, credits in roster:
        p = Player(sport_id=sport.id, full_name=name, team_name=team, role=role, credits=credits, is_active=True)
        db.add(p)
        players.append(p)
    db.flush()
    return sport, players


def test_valid_cricket_team(db):
    _, players = _seed_cricket(db)
    pids = [p.id for p in players]
    v = validate_team(db, sport=SportSlug.cricket,
                      player_ids=pids, captain_id=pids[1], vice_captain_id=pids[2])
    assert v.ok, v.error
    assert v.total_credits <= 100


def test_size_validation(db):
    _, players = _seed_cricket(db)
    pids = [p.id for p in players[:10]]
    v = validate_team(db, sport=SportSlug.cricket,
                      player_ids=pids, captain_id=pids[0], vice_captain_id=pids[1])
    assert not v.ok
    assert "11 players" in (v.error or "")


def test_captain_must_be_in_squad(db):
    _, players = _seed_cricket(db)
    pids = [p.id for p in players]
    v = validate_team(db, sport=SportSlug.cricket,
                      player_ids=pids, captain_id=pids[0], vice_captain_id=pids[0])
    assert not v.ok
