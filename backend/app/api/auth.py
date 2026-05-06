from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_current_user, get_db, get_request_meta
from app.models.responsible import ResponsibleGamingSettings
from app.models.session import UserSession
from app.models.user import KycStatus, User, UserRole
from app.models.wallet import Wallet
from app.schemas.auth import (
    LoginEmail,
    LoginPhone,
    MeOut,
    OtpRequest,
    OtpVerify,
    ProfileUpdate,
    RefreshIn,
    SignupEmail,
    SignupPhone,
    TokenPair,
)
from app.services import otp_service
from app.services.audit_service import write_audit
from app.services.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    gen_referral_code,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _issue_tokens(db: Session, user: User, meta: dict) -> TokenPair:
    refresh, jti = create_refresh_token(str(user.id))
    db.add(
        UserSession(
            user_id=user.id,
            refresh_jti=jti,
            ip=meta.get("ip"),
            user_agent=meta.get("user_agent"),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
        )
    )
    access = create_access_token(str(user.id), user.role.value)
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


def _bootstrap_user(db: Session, user: User) -> None:
    """Ensure wallet + RG settings exist."""
    wallet = db.execute(select(Wallet).where(Wallet.user_id == user.id)).scalar_one_or_none()
    if wallet is None:
        db.add(Wallet(user_id=user.id))
    rg = db.execute(
        select(ResponsibleGamingSettings).where(ResponsibleGamingSettings.user_id == user.id)
    ).scalar_one_or_none()
    if rg is None:
        db.add(ResponsibleGamingSettings(user_id=user.id))


@router.post("/signup/email", response_model=TokenPair, status_code=201)
def signup_email(
    payload: SignupEmail,
    request: Request,
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    if db.execute(select(User).where(User.email == payload.email.lower())).scalar_one_or_none():
        raise HTTPException(409, "email already registered")
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.user,
        kyc_status=KycStatus.none,
        referral_code=gen_referral_code(),
        referred_by_code=payload.referral_code,
    )
    db.add(user)
    db.flush()
    _bootstrap_user(db, user)
    write_audit(db, actor_user_id=user.id, action="auth.signup_email", **meta)
    return _issue_tokens(db, user, meta)


@router.post("/signup/phone", response_model=TokenPair, status_code=201)
def signup_phone(
    payload: SignupPhone,
    request: Request,
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    if db.execute(select(User).where(User.phone == payload.phone)).scalar_one_or_none():
        raise HTTPException(409, "phone already registered")
    user = User(
        phone=payload.phone,
        full_name=payload.full_name,
        role=UserRole.user,
        kyc_status=KycStatus.none,
        referral_code=gen_referral_code(),
        referred_by_code=payload.referral_code,
    )
    db.add(user)
    db.flush()
    _bootstrap_user(db, user)
    otp_service.generate_otp("phone", payload.phone)
    write_audit(db, actor_user_id=user.id, action="auth.signup_phone", **meta)
    return _issue_tokens(db, user, meta)


@router.post("/login/email", response_model=TokenPair)
def login_email(payload: LoginEmail, db: Session = Depends(get_db), meta: dict = Depends(get_request_meta)):
    user = db.execute(select(User).where(User.email == payload.email.lower())).scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "account disabled")
    write_audit(db, actor_user_id=user.id, action="auth.login_email", **meta)
    return _issue_tokens(db, user, meta)


@router.post("/login/phone", response_model=TokenPair)
def login_phone(payload: LoginPhone, db: Session = Depends(get_db), meta: dict = Depends(get_request_meta)):
    if not otp_service.verify_otp("phone", payload.phone, payload.otp):
        raise HTTPException(401, "invalid otp")
    user = db.execute(select(User).where(User.phone == payload.phone)).scalar_one_or_none()
    if user is None:
        user = User(
            phone=payload.phone,
            role=UserRole.user,
            referral_code=gen_referral_code(),
            is_phone_verified=True,
        )
        db.add(user)
        db.flush()
        _bootstrap_user(db, user)
    else:
        user.is_phone_verified = True
    write_audit(db, actor_user_id=user.id, action="auth.login_phone", **meta)
    return _issue_tokens(db, user, meta)


@router.post("/otp/request")
def otp_request(payload: OtpRequest):
    code = otp_service.generate_otp(payload.channel, payload.target)
    return {"sent": True, "dev_code": code if settings.is_dev else None}


@router.post("/otp/verify")
def otp_verify(payload: OtpVerify, db: Session = Depends(get_db)):
    ok = otp_service.verify_otp(payload.channel, payload.target, payload.code)
    if not ok:
        raise HTTPException(401, "invalid otp")
    return {"verified": True}


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, db: Session = Depends(get_db), meta: dict = Depends(get_request_meta)):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(401, "invalid refresh token") from exc
    if decoded.get("type") != "refresh":
        raise HTTPException(401, "wrong token type")

    sess = db.execute(
        select(UserSession).where(UserSession.refresh_jti == decoded["jti"], UserSession.revoked == False)  # noqa: E712
    ).scalar_one_or_none()
    if sess is None:
        raise HTTPException(401, "session not found")
    if sess.expires_at < datetime.now(UTC):
        raise HTTPException(401, "session expired")

    user = db.get(User, sess.user_id)
    if user is None or not user.is_active:
        raise HTTPException(401, "user inactive")
    sess.revoked = True
    return _issue_tokens(db, user, meta)


@router.post("/logout")
def logout(payload: RefreshIn, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception:
        return {"ok": True}
    sess = db.execute(
        select(UserSession).where(UserSession.refresh_jti == decoded.get("jti"))
    ).scalar_one_or_none()
    if sess:
        sess.revoked = True
        db.commit()
    return {"ok": True}


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        username=user.username,
        role=user.role.value,
        kyc_status=user.kyc_status.value,
        state_code=user.state_code,
        referral_code=user.referral_code,
        is_age_verified=user.is_age_verified,
        is_email_verified=user.is_email_verified,
        is_phone_verified=user.is_phone_verified,
    )


@router.patch("/me", response_model=MeOut)
def update_me(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.username is not None:
        user.username = payload.username
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    if payload.state_code is not None:
        user.state_code = payload.state_code.upper()
    if payload.dob is not None:
        from datetime import date

        today = date.today()
        age = today.year - payload.dob.year - ((today.month, today.day) < (payload.dob.month, payload.dob.day))
        if age < 18:
            raise HTTPException(403, "must be 18+ to use this app")
        user.dob = payload.dob
        user.is_age_verified = True
    db.commit()
    return me(user)
