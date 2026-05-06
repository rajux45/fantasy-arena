from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_current_user, get_db, get_request_meta
from app.models.user import KycStatus, User
from app.models.wallet import (
    LedgerEntry,
    Payment,
    PaymentStatus,
    Pocket,
    Withdrawal,
    WithdrawalStatus,
)
from app.schemas.wallet import (
    DepositCreate,
    DepositCreated,
    DepositVerify,
    LedgerRow,
    WalletOut,
    WithdrawalRequest,
)
from app.services import payment_service, wallet_service
from app.services.audit_service import write_audit
from app.services.tax_service import (
    compute_tds_on_withdrawal,
    split_gst_inclusive,
)

router = APIRouter(prefix="/v1/wallet", tags=["wallet"])


@router.get("/me", response_model=WalletOut)
def my_wallet(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = wallet_service.get_wallet(db, user.id)
    return WalletOut(
        deposit_paise=w.deposit_paise,
        winnings_paise=w.winnings_paise,
        bonus_paise=w.bonus_paise,
        casino_coins=w.casino_coins,
        withdrawable_paise=wallet_service.withdrawable_paise(w),
    )


@router.get("/ledger", response_model=list[LedgerRow])
def ledger(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(LedgerEntry)
        .where(LedgerEntry.user_id == user.id)
        .order_by(desc(LedgerEntry.id))
        .limit(min(limit, 200))
        .offset(offset)
    ).scalars().all()
    return [
        LedgerRow(
            id=r.id,
            txn_id=str(r.txn_id),
            account=r.account,
            pocket=r.pocket.value if r.pocket else None,
            amount_paise=r.amount_paise,
            kind=r.kind,
            created_at=r.created_at,
            meta=r.meta,
        )
        for r in rows
    ]


@router.post("/deposits", response_model=DepositCreated, status_code=201)
def create_deposit(
    payload: DepositCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    if payload.amount_paise < settings.deposit_min_paise:
        raise HTTPException(400, "amount below minimum")
    if payload.amount_paise > settings.deposit_max_paise:
        raise HTTPException(400, "amount above maximum")

    if payload.idempotency_key:
        existing = db.execute(
            select(Payment).where(Payment.idempotency_key == payload.idempotency_key)
        ).scalar_one_or_none()
        if existing:
            return DepositCreated(
                payment_id=str(existing.id),
                gateway=existing.gateway,
                gateway_order_id=existing.gateway_order_id or "",
                amount_paise=existing.amount_paise,
                gst_paise=existing.gst_paise,
                net_paise=existing.net_paise,
                key_id=settings.razorpay_key_id or "dev",
            )

    net, gst = split_gst_inclusive(payload.amount_paise)
    order = payment_service.create_razorpay_order(
        amount_paise=payload.amount_paise,
        notes={"user_id": str(user.id), "purpose": "deposit"},
    )

    p = Payment(
        user_id=user.id,
        gateway="razorpay",
        gateway_order_id=order.order_id,
        idempotency_key=payload.idempotency_key,
        amount_paise=payload.amount_paise,
        gst_paise=gst,
        net_paise=net,
        purpose="deposit",
        status=PaymentStatus.created,
    )
    db.add(p)
    db.flush()
    write_audit(db, actor_user_id=user.id, action="wallet.deposit_created",
                target_type="payment", target_id=str(p.id), **meta)
    db.commit()
    return DepositCreated(
        payment_id=str(p.id),
        gateway="razorpay",
        gateway_order_id=order.order_id,
        amount_paise=payload.amount_paise,
        gst_paise=gst,
        net_paise=net,
        key_id=order.key_id,
    )


@router.post("/deposits/verify", response_model=WalletOut)
def verify_deposit(
    payload: DepositVerify,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    payment = db.get(Payment, uuid.UUID(payload.payment_id))
    if payment is None or payment.user_id != user.id:
        raise HTTPException(404, "payment not found")
    if payment.status == PaymentStatus.captured:
        return my_wallet(user, db)

    if not payment_service.verify_payment_signature(
        payload.razorpay_order_id, payload.razorpay_payment_id, payload.razorpay_signature
    ):
        raise HTTPException(400, "invalid signature")

    # Money flow: external bank funds the deposit; user gets net into deposit pocket;
    # the GST portion is moved into a system payable account.
    # Σ legs == 0 (ext:bank_in -amount, user:deposit +net, system:gst_payable +gst).
    legs = [
        wallet_service.Leg(
            account="ext:bank_in", amount_paise=-payment.amount_paise,
            meta={"gateway": "razorpay", "gateway_payment_id": payload.razorpay_payment_id},
        ),
        wallet_service.Leg(
            account=f"user:{user.id}:deposit", amount_paise=payment.net_paise,
            user_id=user.id, pocket=Pocket.deposit,
        ),
    ]
    if payment.gst_paise:
        legs.append(wallet_service.Leg(
            account="system:gst_payable", amount_paise=payment.gst_paise,
        ))

    txn_id = wallet_service.post_txn(db, kind="deposit.captured", legs=legs)
    payment.gateway_payment_id = payload.razorpay_payment_id
    payment.status = PaymentStatus.captured
    write_audit(db, actor_user_id=user.id, action="wallet.deposit_captured",
                target_type="payment", target_id=str(payment.id),
                meta={"txn_id": str(txn_id)}, **meta)
    db.commit()
    return my_wallet(user, db)


@router.post("/withdrawals", status_code=201)
def request_withdrawal(
    payload: WithdrawalRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    meta: dict = Depends(get_request_meta),
):
    if user.kyc_status != KycStatus.verified:
        raise HTTPException(403, "complete KYC before withdrawing")

    w = wallet_service.get_wallet(db, user.id)
    avail = wallet_service.withdrawable_paise(w)
    if payload.amount_paise > avail:
        raise HTTPException(400, "amount exceeds withdrawable balance")

    # TDS calc (simple v1 — uses lifetime numbers; production tracks FY-bounded)
    cum_winnings = sum(
        e.amount_paise
        for e in db.execute(
            select(LedgerEntry).where(
                LedgerEntry.user_id == user.id, LedgerEntry.pocket == Pocket.winnings,
                LedgerEntry.amount_paise > 0,
            )
        ).scalars()
    )
    cum_deposits = sum(
        e.amount_paise
        for e in db.execute(
            select(LedgerEntry).where(
                LedgerEntry.user_id == user.id, LedgerEntry.pocket == Pocket.deposit,
                LedgerEntry.amount_paise > 0,
            )
        ).scalars()
    )
    tds_paid = abs(sum(
        e.amount_paise
        for e in db.execute(
            select(LedgerEntry).where(
                LedgerEntry.user_id == user.id, LedgerEntry.kind == "withdraw.tds",
            )
        ).scalars()
    ))
    tds, payout = compute_tds_on_withdrawal(
        requested_paise=payload.amount_paise,
        cumulative_winnings_paise=cum_winnings,
        cumulative_deposits_paise=cum_deposits,
        tds_already_paid_paise=tds_paid,
    )

    # hold funds: move requested amount from deposit/winnings -> withdraw_holding
    deposit_used = min(w.deposit_paise, payload.amount_paise)
    winnings_used = payload.amount_paise - deposit_used

    wd = Withdrawal(
        user_id=user.id,
        amount_paise=payload.amount_paise,
        tds_paise=tds,
        payout_paise=payout,
        deposit_used_paise=deposit_used,
        winnings_used_paise=winnings_used,
        bank_account_last4=payload.bank_account_last4,
        ifsc=payload.ifsc,
        account_holder=payload.account_holder,
        status=WithdrawalStatus.requested,
    )
    db.add(wd)
    legs = []
    if deposit_used:
        legs.append(wallet_service.Leg(
            account=f"user:{user.id}:deposit", amount_paise=-deposit_used,
            user_id=user.id, pocket=Pocket.deposit,
        ))
    if winnings_used:
        legs.append(wallet_service.Leg(
            account=f"user:{user.id}:winnings", amount_paise=-winnings_used,
            user_id=user.id, pocket=Pocket.winnings,
        ))
    legs.append(wallet_service.Leg(
        account=f"system:withdraw_holding:{user.id}", amount_paise=payload.amount_paise,
    ))
    wallet_service.post_txn(db, kind="withdraw.requested", legs=legs)

    write_audit(db, actor_user_id=user.id, action="wallet.withdraw_requested",
                target_type="withdrawal", target_id=str(wd.id), **meta)
    db.commit()
    return {"id": str(wd.id), "status": wd.status.value, "tds_paise": tds, "payout_paise": payout}
