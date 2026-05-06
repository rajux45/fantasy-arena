from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._mixins import TimestampMixin
from app.models._types import JSONB
from app.models._types import UUID as PgUUID


class KycRecord(Base, TimestampMixin):
    """Stores KYC submissions. PII columns are stored encrypted (Fernet)."""

    __tablename__ = "kyc_records"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    aadhaar_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    aadhaar_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    pan_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    name_on_doc: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selfie_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    vendor: Mapped[str] = mapped_column(String(40), default="manual", nullable=False)
    vendor_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
