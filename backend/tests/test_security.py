from __future__ import annotations

from app.services.security import (
    create_access_token,
    decode_token,
    decrypt_pii,
    encrypt_pii,
    gen_referral_code,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    h = hash_password("super-secret-pw-123")
    assert verify_password("super-secret-pw-123", h)
    assert not verify_password("wrong", h)


def test_password_long_password_under_72_bytes() -> None:
    # bcrypt 72-byte limit must not bite — we sha-256 first.
    long_pw = "a" * 200
    h = hash_password(long_pw)
    assert verify_password(long_pw, h)


def test_jwt_roundtrip() -> None:
    token = create_access_token("user-123", "user")
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "user"
    assert decoded["type"] == "access"


def test_referral_code_uniqueness() -> None:
    codes = {gen_referral_code() for _ in range(200)}
    assert len(codes) > 190  # statistically unique


def test_pii_encryption_dev_pass_through() -> None:
    # No key -> dev pass-through should still round trip
    enc = encrypt_pii("AAAA-BBBB-1234")
    assert decrypt_pii(enc) == "AAAA-BBBB-1234"
