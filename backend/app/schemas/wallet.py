from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WalletOut(BaseModel):
    deposit_paise: int
    winnings_paise: int
    bonus_paise: int
    casino_coins: int
    withdrawable_paise: int


class DepositCreate(BaseModel):
    amount_paise: int = Field(ge=10_000, le=10_000_000)
    promo_code: str | None = None
    idempotency_key: str | None = None


class DepositCreated(BaseModel):
    payment_id: str
    gateway: str
    gateway_order_id: str
    amount_paise: int
    gst_paise: int
    net_paise: int
    key_id: str


class DepositVerify(BaseModel):
    payment_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class WithdrawalRequest(BaseModel):
    amount_paise: int = Field(ge=10_000, le=10_000_000)
    bank_account_last4: str = Field(min_length=4, max_length=4)
    ifsc: str = Field(min_length=11, max_length=11)
    account_holder: str = Field(min_length=2, max_length=120)


class LedgerRow(BaseModel):
    id: int
    txn_id: str
    account: str
    pocket: str | None
    amount_paise: int
    kind: str
    created_at: datetime
    meta: dict | None = None
