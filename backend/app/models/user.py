from __future__ import annotations

import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import UUID as PgUUID


class UserRole(enum.StrEnum):
    user = "user"
    support = "support"
    cms = "cms"
    finance = "finance"
    admin = "admin"
    super_admin = "super_admin"


class KycStatus(enum.StrEnum):
    none = "none"
    pending = "pending"
    in_review = "in_review"
    verified = "verified"
    rejected = "rejected"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("phone", name="uq_users_phone"),
        UniqueConstraint("referral_code", name="uq_users_referral_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    username: Mapped[str | None] = mapped_column(String(40), nullable=True, unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(4), nullable=True, index=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False
    )
    kyc_status: Mapped[KycStatus] = mapped_column(
        Enum(KycStatus, name="kyc_status"), default=KycStatus.none, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_age_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    referral_code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    referred_by_code: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)

    totp_secret_enc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @property
    def primary_identifier(self) -> str:
        return self.email or self.phone or str(self.id)
