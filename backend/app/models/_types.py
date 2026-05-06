"""Cross-dialect column types: JSONB on Postgres, JSON on SQLite; UUID on Postgres, CHAR(36) on SQLite."""
from __future__ import annotations

import uuid as _uuid

from sqlalchemy import CHAR, JSON
from sqlalchemy.dialects.postgresql import JSONB as PgJSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.types import TypeDecorator


class JSONB(TypeDecorator):
    """Dialect-aware JSONB. Stores native jsonb on Postgres, JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgJSONB())
        return dialect.type_descriptor(JSON())


class UUID(TypeDecorator):
    """Dialect-aware UUID. Stores native uuid on Postgres, 36-char string on others."""

    impl = CHAR(36)
    cache_ok = True

    def __init__(self, *args, as_uuid: bool = True, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        if isinstance(value, _uuid.UUID):
            return str(value)
        return str(_uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, _uuid.UUID):
            return value
        try:
            return _uuid.UUID(str(value))
        except Exception:
            return value
