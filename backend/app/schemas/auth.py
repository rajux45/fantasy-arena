from __future__ import annotations

from datetime import date

from pydantic import BaseModel, EmailStr, Field


class SignupEmail(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)
    referral_code: str | None = None


class SignupPhone(BaseModel):
    phone: str = Field(min_length=10, max_length=15)
    full_name: str | None = Field(default=None, max_length=120)
    referral_code: str | None = None


class LoginEmail(BaseModel):
    email: EmailStr
    password: str


class LoginPhone(BaseModel):
    phone: str
    otp: str = Field(min_length=4, max_length=8)


class OtpRequest(BaseModel):
    channel: str = Field(pattern="^(phone|email)$")
    target: str


class OtpVerify(BaseModel):
    channel: str = Field(pattern="^(phone|email)$")
    target: str
    code: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class MeOut(BaseModel):
    id: str
    email: str | None
    phone: str | None
    full_name: str | None
    username: str | None
    role: str
    kyc_status: str
    state_code: str | None
    referral_code: str
    is_age_verified: bool
    is_email_verified: bool
    is_phone_verified: bool


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    username: str | None = Field(default=None, min_length=3, max_length=40)
    avatar_url: str | None = None
    state_code: str | None = Field(default=None, max_length=4)
    dob: date | None = None
