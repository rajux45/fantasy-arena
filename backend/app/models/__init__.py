"""SQLAlchemy ORM models. Importing this package registers all tables on Base.metadata."""
from __future__ import annotations

from app.models.audit import AuditLog
from app.models.casino import CasinoGame, CasinoRound, CasinoSeed
from app.models.contest import Contest, ContestEntry, PrizeSlab
from app.models.kyc import KycRecord
from app.models.match import Match, MatchPlayerStats
from app.models.notification import Notification
from app.models.player import Player
from app.models.promo import CashbackRule, PromoCode, Referral
from app.models.responsible import ResponsibleGamingSettings, SelfExclusion
from app.models.session import UserSession
from app.models.sport import Sport, Tournament
from app.models.team import UserTeam, UserTeamPlayer
from app.models.user import User
from app.models.wallet import LedgerEntry, Payment, Wallet, Withdrawal

__all__ = [
    "AuditLog",
    "CashbackRule",
    "CasinoGame",
    "CasinoRound",
    "CasinoSeed",
    "Contest",
    "ContestEntry",
    "KycRecord",
    "LedgerEntry",
    "Match",
    "MatchPlayerStats",
    "Notification",
    "Payment",
    "Player",
    "PrizeSlab",
    "PromoCode",
    "Referral",
    "ResponsibleGamingSettings",
    "SelfExclusion",
    "Sport",
    "Tournament",
    "User",
    "UserSession",
    "UserTeam",
    "UserTeamPlayer",
    "Wallet",
    "Withdrawal",
]
