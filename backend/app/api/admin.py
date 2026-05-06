from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.deps import get_admin_user, get_db, get_request_meta
from app.models.kyc import KycRecord
from app.models.user import KycStatus, User, UserRole
from app.models.wallet import Pocket, Withdrawal, WithdrawalStatus
from app.schemas.admin import (
    KycReviewIn,
    ManualWalletAdjust,
    UserAdminRow,
    WithdrawalApproveIn,
    WithdrawalRejectIn,
)
from app.services import wallet_service
from app.services.audit_service import write_audit

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/users", response_model=list[UserAdminRow])
def list_users(
    q: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    sel = select(User)
    if q:
        like = f"%{q}%"
        sel = sel.where((User.email.ilike(like)) | (User.phone.ilike(like)) | (User.full_name.ilike(like)))
    rows = db.execute(sel.order_by(desc(User.created_at)).limit(200)).scalars().all()
    return [
        UserAdminRow(
            id=u.id, email=u.email, phone=u.phone, full_name=u.full_name,
            role=u.role.value, kyc_status=u.kyc_status.value, state_code=u.state_code,
            is_active=u.is_active, created_at=u.created_at,
        )
        for u in rows
    ]


@router.post("/users/{user_id}/ban")
def ban(
    user_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(404, "user not found")
    if u.role == UserRole.super_admin:
        raise HTTPException(403, "cannot ban super_admin")
    u.is_active = False
    write_audit(db, actor_user_id=actor.id, action="admin.user_ban",
                target_type="user", target_id=str(u.id), **meta)
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/unban")
def unban(
    user_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(404, "user not found")
    u.is_active = True
    write_audit(db, actor_user_id=actor.id, action="admin.user_unban",
                target_type="user", target_id=str(u.id), **meta)
    db.commit()
    return {"ok": True}


@router.get("/kyc/queue")
def kyc_queue(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    rows = db.execute(
        select(KycRecord).where(KycRecord.status.in_(["pending", "in_review"])).order_by(KycRecord.created_at)
    ).scalars().all()
    return [
        {
            "id": str(r.id),
            "user_id": str(r.user_id),
            "aadhaar_last4": r.aadhaar_last4,
            "name_on_doc": r.name_on_doc,
            "selfie_url": r.selfie_url,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/kyc/{kyc_id}/review")
def review_kyc(
    kyc_id: UUID,
    payload: KycReviewIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    rec = db.get(KycRecord, kyc_id)
    if rec is None:
        raise HTTPException(404, "kyc record not found")
    user = db.get(User, rec.user_id)
    if user is None:
        raise HTTPException(404, "user not found")
    if payload.approve:
        rec.status = "approved"
        user.kyc_status = KycStatus.verified
    else:
        rec.status = "rejected"
        rec.rejection_reason = payload.reason
        user.kyc_status = KycStatus.rejected
    write_audit(db, actor_user_id=actor.id, action="admin.kyc_review",
                target_type="kyc", target_id=str(rec.id),
                meta={"approve": payload.approve, "reason": payload.reason}, **meta)
    db.commit()
    return {"ok": True, "status": rec.status}


@router.get("/withdrawals/queue")
def withdrawal_queue(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    rows = db.execute(
        select(Withdrawal).where(Withdrawal.status.in_([WithdrawalStatus.requested, WithdrawalStatus.in_review]))
        .order_by(Withdrawal.created_at)
    ).scalars().all()
    return [
        {
            "id": str(w.id),
            "user_id": str(w.user_id),
            "amount_paise": w.amount_paise,
            "tds_paise": w.tds_paise,
            "payout_paise": w.payout_paise,
            "status": w.status.value,
            "ifsc": w.ifsc,
            "account_holder": w.account_holder,
            "bank_account_last4": w.bank_account_last4,
            "created_at": w.created_at.isoformat(),
        }
        for w in rows
    ]


@router.post("/withdrawals/{withdrawal_id}/approve")
def approve_withdrawal(
    withdrawal_id: UUID,
    payload: WithdrawalApproveIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    wd = db.get(Withdrawal, withdrawal_id)
    if wd is None:
        raise HTTPException(404, "withdrawal not found")
    if wd.status not in {WithdrawalStatus.requested, WithdrawalStatus.in_review}:
        raise HTTPException(400, "invalid status transition")

    # Move from holding to bank_out + record TDS
    legs = [
        wallet_service.Leg(
            account=f"system:withdraw_holding:{wd.user_id}", amount_paise=-wd.amount_paise,
        ),
        wallet_service.Leg(account="ext:bank_out", amount_paise=wd.payout_paise,
                           meta={"withdrawal_id": str(wd.id)}),
    ]
    if wd.tds_paise:
        legs.append(wallet_service.Leg(account="system:tds_payable", amount_paise=wd.tds_paise))
    wallet_service.post_txn(db, kind="withdraw.tds" if wd.tds_paise else "withdraw.approved", legs=legs)

    wd.status = WithdrawalStatus.approved
    wd.reviewed_by = actor.id
    write_audit(db, actor_user_id=actor.id, action="admin.withdrawal_approved",
                target_type="withdrawal", target_id=str(wd.id), **meta)
    db.commit()
    return {"ok": True}


@router.post("/withdrawals/{withdrawal_id}/reject")
def reject_withdrawal(
    withdrawal_id: UUID,
    payload: WithdrawalRejectIn,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    wd = db.get(Withdrawal, withdrawal_id)
    if wd is None:
        raise HTTPException(404, "withdrawal not found")
    if wd.status not in {WithdrawalStatus.requested, WithdrawalStatus.in_review}:
        raise HTTPException(400, "invalid status transition")

    # Restore balance to original pockets so deposit / winnings split is preserved.
    legs: list[wallet_service.Leg] = [
        wallet_service.Leg(
            account=f"system:withdraw_holding:{wd.user_id}", amount_paise=-wd.amount_paise,
        ),
    ]
    if wd.deposit_used_paise:
        legs.append(wallet_service.Leg(
            account=f"user:{wd.user_id}:deposit", amount_paise=wd.deposit_used_paise,
            user_id=wd.user_id, pocket=Pocket.deposit,
        ))
    if wd.winnings_used_paise:
        legs.append(wallet_service.Leg(
            account=f"user:{wd.user_id}:winnings", amount_paise=wd.winnings_used_paise,
            user_id=wd.user_id, pocket=Pocket.winnings,
        ))
    # Backwards-compat: legacy rows where pocket breakdown was not recorded
    # restore the entire amount to the deposit pocket (matches previous behaviour).
    if not wd.deposit_used_paise and not wd.winnings_used_paise and wd.amount_paise:
        legs.append(wallet_service.Leg(
            account=f"user:{wd.user_id}:deposit", amount_paise=wd.amount_paise,
            user_id=wd.user_id, pocket=Pocket.deposit,
        ))
    wallet_service.post_txn(db, kind="withdraw.rejected", legs=legs)
    wd.status = WithdrawalStatus.rejected
    wd.rejection_reason = payload.reason
    write_audit(db, actor_user_id=actor.id, action="admin.withdrawal_rejected",
                target_type="withdrawal", target_id=str(wd.id),
                meta={"reason": payload.reason}, **meta)
    db.commit()
    return {"ok": True}


@router.post("/wallet/manual-adjust")
def manual_adjust(
    payload: ManualWalletAdjust,
    db: Session = Depends(get_db),
    actor: User = Depends(get_admin_user),
    meta: dict = Depends(get_request_meta),
):
    if not payload.reason or len(payload.reason) < 5:
        raise HTTPException(400, "reason required (min 5 chars)")
    pocket = Pocket(payload.pocket)
    legs = [
        wallet_service.Leg(
            account=f"user:{payload.user_id}:{payload.pocket}",
            amount_paise=payload.amount_paise,
            user_id=payload.user_id,
            pocket=pocket,
        ),
        wallet_service.Leg(
            account=f"system:manual_adjust:{actor.id}",
            amount_paise=-payload.amount_paise,
        ),
    ]
    wallet_service.post_txn(db, kind="wallet.manual_adjust", legs=legs)
    write_audit(db, actor_user_id=actor.id, action="admin.wallet_manual_adjust",
                target_type="user", target_id=str(payload.user_id),
                meta={"amount_paise": payload.amount_paise, "pocket": payload.pocket,
                       "reason": payload.reason}, **meta)
    db.commit()
    return {"ok": True}
