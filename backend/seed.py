"""Seed the database with demo data: sports, players, matches, contests, an admin user, promo codes."""
from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models.casino import CasinoGame, CasinoGameSlug
from app.models.contest import Contest, ContestKind, PrizeSlab
from app.models.match import Match, MatchStatus
from app.models.player import Player, PlayerRole
from app.models.promo import CashbackRule, PromoCode, PromoKind
from app.models.sport import Sport, SportSlug, Tournament
from app.models.user import KycStatus, User, UserRole
from app.models.wallet import Wallet
from app.services.security import gen_referral_code, hash_password

random.seed(42)


def reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def seed_sports(db: Session) -> dict[SportSlug, Sport]:
    sports: dict[SportSlug, Sport] = {}
    for slug, name in [
        (SportSlug.cricket, "Cricket"),
        (SportSlug.football, "Football"),
        (SportSlug.kabaddi, "Kabaddi"),
        (SportSlug.basketball, "Basketball"),
    ]:
        s = Sport(slug=slug, name=name, is_active=True)
        db.add(s)
        sports[slug] = s
    db.flush()
    return sports


def seed_casino(db: Session) -> None:
    for slug in CasinoGameSlug:
        db.add(CasinoGame(slug=slug, name=slug.value.title(), house_edge_bp=200, is_active=True))
    db.flush()


CRICKET_PLAYERS = [
    ("Rohit Sharma", "MI", PlayerRole.batsman, 10.5),
    ("Ishan Kishan", "MI", PlayerRole.wicket_keeper, 9.0),
    ("Suryakumar Yadav", "MI", PlayerRole.batsman, 10.0),
    ("Hardik Pandya", "MI", PlayerRole.all_rounder, 10.5),
    ("Tilak Varma", "MI", PlayerRole.batsman, 8.5),
    ("Tim David", "MI", PlayerRole.batsman, 8.5),
    ("Cameron Green", "MI", PlayerRole.all_rounder, 9.0),
    ("Jasprit Bumrah", "MI", PlayerRole.bowler, 10.5),
    ("Piyush Chawla", "MI", PlayerRole.bowler, 8.0),
    ("Akash Madhwal", "MI", PlayerRole.bowler, 7.5),
    ("Romario Shepherd", "MI", PlayerRole.all_rounder, 8.5),
    ("MS Dhoni", "CSK", PlayerRole.wicket_keeper, 9.5),
    ("Ruturaj Gaikwad", "CSK", PlayerRole.batsman, 10.5),
    ("Devon Conway", "CSK", PlayerRole.batsman, 9.5),
    ("Ajinkya Rahane", "CSK", PlayerRole.batsman, 8.5),
    ("Shivam Dube", "CSK", PlayerRole.all_rounder, 9.5),
    ("Ravindra Jadeja", "CSK", PlayerRole.all_rounder, 10.5),
    ("Moeen Ali", "CSK", PlayerRole.all_rounder, 9.0),
    ("Deepak Chahar", "CSK", PlayerRole.bowler, 9.0),
    ("Tushar Deshpande", "CSK", PlayerRole.bowler, 8.0),
    ("Matheesha Pathirana", "CSK", PlayerRole.bowler, 9.0),
    ("Mustafizur Rahman", "CSK", PlayerRole.bowler, 8.5),
]

FOOTBALL_PLAYERS = [
    ("Sunil Chhetri", "BFC", PlayerRole.forward, 10.5),
    ("Gurpreet Singh Sandhu", "BFC", PlayerRole.goalkeeper, 9.0),
    ("Sandesh Jhingan", "BFC", PlayerRole.defender, 9.0),
    ("Roshan Singh", "BFC", PlayerRole.defender, 8.5),
    ("Suresh Wangjam", "BFC", PlayerRole.midfielder, 8.5),
    ("Bruno Ramires", "BFC", PlayerRole.midfielder, 9.5),
    ("Pablo Pérez", "BFC", PlayerRole.midfielder, 9.0),
    ("Javier Hernández", "BFC", PlayerRole.midfielder, 9.0),
    ("Jérémy Manzorro", "BFC", PlayerRole.midfielder, 9.0),
    ("Chinglensana Singh", "BFC", PlayerRole.defender, 8.0),
    ("Naorem Roshan Singh", "BFC", PlayerRole.defender, 8.0),
    ("Bipin Singh", "MUM", PlayerRole.forward, 10.0),
    ("Phurba Lachenpa", "MUM", PlayerRole.goalkeeper, 8.5),
    ("Mehtab Singh", "MUM", PlayerRole.defender, 8.5),
    ("Rahul Bheke", "MUM", PlayerRole.defender, 8.5),
    ("Lallianzuala Chhangte", "MUM", PlayerRole.midfielder, 9.5),
    ("Vikram Pratap Singh", "MUM", PlayerRole.midfielder, 9.0),
    ("Jorge Pereyra Díaz", "MUM", PlayerRole.forward, 9.5),
    ("Greg Stewart", "MUM", PlayerRole.midfielder, 9.5),
    ("Thaer Krouma", "MUM", PlayerRole.defender, 8.0),
    ("Holicharan Narzary", "MUM", PlayerRole.midfielder, 8.5),
    ("Ahmed Jahouh", "MUM", PlayerRole.midfielder, 9.0),
]

KABADDI_PLAYERS = [
    ("Pardeep Narwal", "PUNERI", PlayerRole.raider, 10.5),
    ("Aslam Inamdar", "PUNERI", PlayerRole.raider, 9.0),
    ("Mohit Goyat", "PUNERI", PlayerRole.raider, 9.0),
    ("Fazel Atrachali", "PUNERI", PlayerRole.defender_kabaddi, 10.0),
    ("Sanket Sawant", "PUNERI", PlayerRole.defender_kabaddi, 8.5),
    ("Sombir", "PUNERI", PlayerRole.defender_kabaddi, 8.5),
    ("Vishwas S.", "PUNERI", PlayerRole.all_rounder_kabaddi, 8.5),
    ("Pawan Sehrawat", "JAIPUR", PlayerRole.raider, 10.5),
    ("Arjun Deshwal", "JAIPUR", PlayerRole.raider, 10.0),
    ("V. Ajith Kumar", "JAIPUR", PlayerRole.raider, 8.5),
    ("Ankush Rathee", "JAIPUR", PlayerRole.defender_kabaddi, 9.0),
    ("Sahul Kumar", "JAIPUR", PlayerRole.defender_kabaddi, 8.5),
    ("Sunil Kumar", "JAIPUR", PlayerRole.defender_kabaddi, 8.5),
    ("Reza Mirbagheri", "JAIPUR", PlayerRole.all_rounder_kabaddi, 8.0),
]

BASKETBALL_PLAYERS = [
    ("Rikin Pethani", "BLR", PlayerRole.center, 10.5),
    ("Yadwinder Singh", "BLR", PlayerRole.power_forward, 9.5),
    ("Aman Mishra", "BLR", PlayerRole.point_guard, 9.0),
    ("Vishesh Bhriguvanshi", "BLR", PlayerRole.shooting_guard, 10.0),
    ("Joginder Singh", "BLR", PlayerRole.small_forward, 8.5),
    ("Pratham Singh", "BLR", PlayerRole.point_guard, 8.0),
    ("Akilan Pari", "DEL", PlayerRole.point_guard, 9.0),
    ("Riyanshu Negi", "DEL", PlayerRole.shooting_guard, 9.0),
    ("Aravind Annadurai", "DEL", PlayerRole.center, 9.5),
    ("Loveneet Singh", "DEL", PlayerRole.power_forward, 9.0),
    ("Arvind Kumar", "DEL", PlayerRole.small_forward, 8.5),
    ("Jagdeep Singh", "DEL", PlayerRole.center, 8.5),
]


def seed_players(db: Session, sports: dict[SportSlug, Sport]) -> dict[SportSlug, list[Player]]:
    out: dict[SportSlug, list[Player]] = {}
    rosters = {
        SportSlug.cricket: CRICKET_PLAYERS,
        SportSlug.football: FOOTBALL_PLAYERS,
        SportSlug.kabaddi: KABADDI_PLAYERS,
        SportSlug.basketball: BASKETBALL_PLAYERS,
    }
    for slug, roster in rosters.items():
        sport = sports[slug]
        ps: list[Player] = []
        for name, team, role, credits in roster:
            p = Player(
                sport_id=sport.id,
                full_name=name,
                short_name=name.split()[-1],
                team_name=team,
                role=role,
                credits=Decimal(str(credits)),
                is_active=True,
            )
            db.add(p)
            ps.append(p)
        db.flush()
        out[slug] = ps
    return out


def seed_matches_and_contests(db: Session, sports: dict[SportSlug, Sport]) -> None:
    now = datetime.now(UTC)
    fixtures = [
        (SportSlug.cricket, "MI vs CSK", "MI", "CSK", "Wankhede"),
        (SportSlug.football, "BFC vs MUM", "BFC", "MUM", "Sree Kanteerava"),
        (SportSlug.kabaddi, "PUNERI vs JAIPUR", "PUNERI", "JAIPUR", "BR Ambedkar Stadium"),
        (SportSlug.basketball, "BLR vs DEL", "BLR", "DEL", "Indira Gandhi Indoor"),
    ]
    for sport_slug, short_name, home, away, venue in fixtures:
        sport = sports[sport_slug]
        tour = Tournament(sport_id=sport.id, name=f"{sport.name} Demo League", season="2025-26")
        db.add(tour)
        db.flush()
        starts = now + timedelta(hours=24)
        m = Match(
            tournament_id=tour.id,
            sport_id=sport.id,
            short_name=short_name,
            home_team=home,
            away_team=away,
            venue=venue,
            starts_at=starts,
            lineup_locks_at=starts - timedelta(minutes=15),
            status=MatchStatus.upcoming,
        )
        db.add(m)
        db.flush()

        # Mega contest
        mega = Contest(
            match_id=m.id,
            name=f"{short_name} Mega Contest",
            kind=ContestKind.mega,
            entry_fee_paise=4900,  # ₹49
            prize_pool_paise=4_00_000,  # ₹4,000
            total_slots=100,
            max_teams_per_user=20,
            guaranteed=True,
            rake_pct=Decimal("18.0"),
        )
        db.add(mega)
        db.flush()
        db.add_all([
            PrizeSlab(contest_id=mega.id, rank_from=1, rank_to=1, prize_paise=1_50_000),
            PrizeSlab(contest_id=mega.id, rank_from=2, rank_to=2, prize_paise=80_000),
            PrizeSlab(contest_id=mega.id, rank_from=3, rank_to=3, prize_paise=40_000),
            PrizeSlab(contest_id=mega.id, rank_from=4, rank_to=10, prize_paise=10_000),
            PrizeSlab(contest_id=mega.id, rank_from=11, rank_to=30, prize_paise=5_000),
        ])

        # H2H contest
        h2h = Contest(
            match_id=m.id,
            name=f"{short_name} Head-to-Head",
            kind=ContestKind.head_to_head,
            entry_fee_paise=9900,
            prize_pool_paise=18_000,
            total_slots=2,
            max_teams_per_user=1,
            rake_pct=Decimal("9.0"),
        )
        db.add(h2h)
        db.flush()
        db.add(PrizeSlab(contest_id=h2h.id, rank_from=1, rank_to=1, prize_paise=18_000))

        # Practice contest (free)
        practice = Contest(
            match_id=m.id,
            name=f"{short_name} Practice",
            kind=ContestKind.practice,
            entry_fee_paise=0,
            prize_pool_paise=0,
            total_slots=1000,
            max_teams_per_user=20,
            rake_pct=Decimal("0.0"),
        )
        db.add(practice)
    db.flush()


def seed_admin(db: Session) -> User:
    admin = User(
        email="admin@fantasy-arena.example",
        password_hash=hash_password("Admin@12345"),
        full_name="Admin",
        role=UserRole.super_admin,
        kyc_status=KycStatus.verified,
        is_email_verified=True,
        is_age_verified=True,
        referral_code=gen_referral_code(),
        state_code="MH",
    )
    db.add(admin)
    db.flush()
    db.add(Wallet(user_id=admin.id))
    db.flush()
    return admin


def seed_promos(db: Session) -> None:
    db.add_all([
        PromoCode(code="WELCOME100", kind=PromoKind.flat_bonus, value_paise=10_000,
                  min_deposit_paise=10_000, max_bonus_paise=10_000, usage_limit=100000,
                  per_user_limit=1, is_active=True),
        PromoCode(code="MATCH50", kind=PromoKind.deposit_match, value_pct=Decimal("50"),
                  min_deposit_paise=50_000, max_bonus_paise=1_00_000, usage_limit=100000,
                  per_user_limit=1, is_active=True),
    ])
    db.add(CashbackRule(name="Weekly fantasy cashback", threshold_paise=2_00_000,
                        cashback_pct=Decimal("5"), cap_paise=50_000, period="weekly", is_active=True))


def main() -> None:
    print("creating schema…")
    reset_schema()
    db = SessionLocal()
    try:
        sports = seed_sports(db)
        seed_casino(db)
        players = seed_players(db, sports)
        seed_matches_and_contests(db, sports)
        seed_admin(db)
        seed_promos(db)
        db.commit()
        print(f"seeded {sum(len(v) for v in players.values())} players across "
              f"{len(sports)} sports")
        print("admin login: admin@fantasy-arena.example / Admin@12345")
    finally:
        db.close()


if __name__ == "__main__":
    main()
