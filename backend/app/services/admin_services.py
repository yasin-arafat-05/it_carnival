import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, or_, and_, desc, text
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.locks import LOCK_MANAGER
from app.database.models.user import User
from app.database.models.account import Account
from app.database.models.transaction import Transaction
from app.database.models.ledger import LedgerEntry
from app.database.models.notification import Notification
from app.database.models.dispute import Dispute
from app.database.schemas.transaction import TransactionResponse
from app.database.schemas.dispute import DisputeResponse, DisputeResolveAction
from app.services.wallet_services import build_transaction_response
from app.services.dispute_services import build_dispute_response


async def get_all_system_transactions(
    page: int, limit: int, search: Optional[str], db: AsyncSession
) -> List[TransactionResponse]:
    """
    Fetches system-wide transaction history for Admin inspection with filtering.

    Args:
        page (int): Page number (1-indexed).
        limit (int): Items per page.
        search (Optional[str]): Search term for reference_id or username.
        db (AsyncSession): Database session.

    Returns:
        List[TransactionResponse]: List of system transaction records.
    """
    offset = (page - 1) * limit
    query = (
        select(Transaction)
        .options(
            joinedload(Transaction.sender_account).joinedload(Account.user),
            joinedload(Transaction.receiver_account).joinedload(Account.user),
        )
        .order_by(desc(Transaction.created_at))
    )

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Transaction.reference_id.ilike(term),
                Transaction.sender_account.has(Account.user.has(User.username.ilike(term))),
                Transaction.receiver_account.has(Account.user.has(User.username.ilike(term))),
            )
        )

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()
    return [build_transaction_response(tx) for tx in transactions]


async def get_all_disputes(
    status_filter: Optional[str], db: AsyncSession
) -> List[DisputeResponse]:
    """
    Retrieves all disputes and false transaction reversal requests system-wide.

    Args:
        status_filter (Optional[str]): Optional status filter string.
        db (AsyncSession): Database session.

    Returns:
        List[DisputeResponse]: List of disputes.
    """
    query = (
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .order_by(desc(Dispute.created_at))
    )

    if status_filter and status_filter.strip():
        query = query.where(Dispute.status == status_filter.strip())

    result = await db.execute(query)
    disputes = result.scalars().all()
    return [build_dispute_response(d) for d in disputes]


async def execute_admin_reversal(
    admin_user: User, dispute_id: uuid.UUID, admin_notes: Optional[str], db: AsyncSession
) -> DisputeResponse:
    """
    Executes an atomic money reversal (refund) for a confirmed false transaction or approved dispute.
    Debits receiver, credits sender, creates reversal transaction and ledger entries.

    Args:
        admin_user (User): Admin executing reversal.
        dispute_id (UUID): Dispute primary key.
        admin_notes (Optional[str]): Execution memo.
        db (AsyncSession): Database session.

    Returns:
        DisputeResponse: Updated dispute object with RESOLVED_REVERSED status.
    """
    lock_key = f"execute_reversal_{dispute_id}"
    thread_lock = LOCK_MANAGER.get_lock(lock_key)

    with thread_lock:
        query = (
            select(Dispute)
            .options(
                joinedload(Dispute.transaction),
                joinedload(Dispute.sender),
                joinedload(Dispute.receiver),
            )
            .where(Dispute.id == dispute_id)
            .with_for_update()
        )
        result = await db.execute(query)
        dispute = result.scalar_one_or_none()

        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute record not found.",
            )

        if dispute.status in ("RESOLVED_REVERSED", "REJECTED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dispute is already resolved with status '{dispute.status}'.",
            )

        tx = dispute.transaction
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated transaction record not found.",
            )

        # Fetch Sender and Receiver Wallet Accounts
        sender_acc_res = await db.execute(select(Account).where(Account.user_id == dispute.sender_id).with_for_update())
        sender_acc = sender_acc_res.scalar_one_or_none()

        receiver_acc_res = await db.execute(select(Account).where(Account.user_id == dispute.receiver_id).with_for_update())
        receiver_acc = receiver_acc_res.scalar_one_or_none()

        if not sender_acc or not receiver_acc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender or receiver wallet account not found.",
            )

        reversal_amount = tx.amount

        if receiver_acc.available_balance < reversal_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Receiver account does not have sufficient balance (BDT {receiver_acc.available_balance:,.2f}) to complete reversal of BDT {reversal_amount:,.2f}.",
            )

        # 1. Execute Atomic Balance Movement (Refund receiver -> sender)
        receiver_acc.balance -= reversal_amount
        receiver_acc.available_balance -= reversal_amount

        sender_acc.balance += reversal_amount
        sender_acc.available_balance += reversal_amount

        # 2. Record Reversal Transaction
        now_str = datetime.utcnow().strftime("%Y%m%d")
        rev_ref = f"REV-{now_str}-{uuid.uuid4().hex[:6].upper()}"
        reversal_tx = Transaction(
            reference_id=rev_ref,
            sender_account_id=receiver_acc.id,
            receiver_account_id=sender_acc.id,
            amount=reversal_amount,
            currency="BDT",
            transaction_type="REVERSAL",
            status="COMPLETED",
            note=f"Admin false transaction reversal for dispute {dispute.id}",
        )
        db.add(reversal_tx)
        await db.flush()

        # 3. Create Double-Entry Ledger Records
        receiver_ledger = LedgerEntry(
            transaction_id=reversal_tx.id,
            account_id=receiver_acc.id,
            entry_type="DEBIT",
            amount=reversal_amount,
            balance_after=receiver_acc.balance,
        )
        sender_ledger = LedgerEntry(
            transaction_id=reversal_tx.id,
            account_id=sender_acc.id,
            entry_type="CREDIT",
            amount=reversal_amount,
            balance_after=sender_acc.balance,
        )
        db.add_all([receiver_ledger, sender_ledger])

        # 4. Update Dispute Status
        dispute.status = "RESOLVED_REVERSED"
        dispute.admin_notes = admin_notes or f"Reversal executed by Admin {admin_user.username} (Ref: {rev_ref})"

        # 5. Dispatch Notifications
        sender_notif = Notification(
            user_id=dispute.sender_id,
            title="False Transaction Refunded",
            message=f"Admin has approved your false transaction reversal. BDT {reversal_amount:,.2f} refunded to your account.",
            notification_type="REVERSAL_COMPLETED",
            reference_id=rev_ref,
        )
        receiver_notif = Notification(
            user_id=dispute.receiver_id,
            title="Transaction Reversed",
            message=f"Admin executed reversal for false transaction {tx.reference_id}. BDT {reversal_amount:,.2f} debited.",
            notification_type="REVERSAL_COMPLETED",
            reference_id=rev_ref,
        )
        db.add_all([sender_notif, receiver_notif])

        await db.commit()
        await db.refresh(dispute)
        return build_dispute_response(dispute)


async def resolve_dispute_complaint(
    admin_user: User,
    dispute_id: uuid.UUID,
    resolve_data: DisputeResolveAction,
    db: AsyncSession,
) -> DisputeResponse:
    """
    Handles formal complaint dispute resolution by Admin (Long Process).

    Args:
        admin_user (User): Admin user.
        dispute_id (UUID): Dispute ID.
        resolve_data (DisputeResolveAction): Resolution payload.
        db (AsyncSession): Database session.

    Returns:
        DisputeResponse: Resolved dispute object.
    """
    if resolve_data.decision == "APPROVE_REVERSAL":
        return await execute_admin_reversal(
            admin_user=admin_user,
            dispute_id=dispute_id,
            admin_notes=resolve_data.admin_notes,
            db=db,
        )

    # If REJECT
    query = select(Dispute).where(Dispute.id == dispute_id)
    res = await db.execute(query)
    dispute = res.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found.")

    dispute.status = "REJECTED"
    dispute.admin_notes = resolve_data.admin_notes or f"Complaint rejected after investigation by Admin {admin_user.username}"

    # Notify sender
    notif = Notification(
        user_id=dispute.sender_id,
        title="Dispute Complaint Closed",
        message=f"Admin investigated complaint for transaction {dispute.transaction_id} and decided: REJECTED.",
        notification_type="DISPUTE_CLOSED",
        reference_id=str(dispute.id),
    )
    db.add(notif)

    await db.commit()
    await db.refresh(dispute)
    return build_dispute_response(dispute)


async def assign_user_admin_role(
    target_username: str, db: AsyncSession
) -> dict:
    """
    Promotes a user to ADMIN role.

    Args:
        target_username (str): Username handle to promote.
        db (AsyncSession): Database session.

    Returns:
        dict: Confirmation message.
    """
    query = select(User).where(User.username == target_username)
    res = await db.execute(query)
    target_user = res.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{target_username}' not found.",
        )

    target_user.role = "ADMIN"
    await db.commit()
    return {"message": f"User '{target_username}' promoted to ADMIN successfully."}
