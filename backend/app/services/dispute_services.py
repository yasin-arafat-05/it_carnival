import uuid
from typing import List, Optional
from sqlalchemy import select, or_, and_, desc
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.models.transaction import Transaction
from app.database.models.dispute import Dispute
from app.database.models.notification import Notification
from app.database.schemas.dispute import (
    FalseTransactionRequest,
    ComplaintRequest,
    DisputeReceiverAction,
    DisputeResponse,
)


def build_dispute_response(dispute: Dispute) -> DisputeResponse:
    """
    Constructs DisputeResponse schema populating usernames, reference ID, and transaction amount.

    Args:
        dispute (Dispute): Dispute ORM instance.

    Returns:
        DisputeResponse: Populated Pydantic schema.
    """
    res = DisputeResponse.model_validate(dispute)

    if getattr(dispute, "transaction", None):
        res.transaction_reference = dispute.transaction.reference_id
        res.amount = dispute.transaction.amount

    if getattr(dispute, "sender", None):
        res.sender_username = dispute.sender.username

    if getattr(dispute, "receiver", None):
        res.receiver_username = dispute.receiver.username

    return res


async def create_false_transaction_request(
    sender_user: User, request_data: FalseTransactionRequest, db: AsyncSession
) -> DisputeResponse:
    """
    Initiates a mutual false transaction reversal request.
    Creates a dispute entry with status PENDING_RECEIVER_CONFIRMATION and notifies the receiver.

    Args:
        sender_user (User): Authenticated sender user.
        request_data (FalseTransactionRequest): Payload containing transaction_reference and reason.
        db (AsyncSession): Database session.

    Returns:
        DisputeResponse: Created dispute object.
    """
    if sender_user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users are restricted from creating false transaction reversal claims.",
        )

    # 1. Resolve Transaction by Reference ID
    tx_query = select(Transaction).where(Transaction.reference_id == request_data.transaction_reference)
    tx_res = await db.execute(tx_query)
    tx = tx_res.scalar_one_or_none()

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with reference '{request_data.transaction_reference}' not found.",
        )

    # 2. Verify current user is the sender of this transaction
    sender_acc_res = await db.execute(select(User).where(User.id == sender_user.id).options(joinedload(User.account)))
    usr = sender_acc_res.scalar_one()

    if not usr.account or tx.sender_account_id != usr.account.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request false transaction reversals for transfers you sent.",
        )

    # 3. Fetch Receiver User
    receiver_acc_res = await db.execute(select(User).where(User.account.has(id=tx.receiver_account_id)))
    receiver_user = receiver_acc_res.scalar_one_or_none()

    if not receiver_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver account for this transaction could not be located.",
        )

    # 4. Check for existing open dispute on this transaction
    existing = await db.execute(select(Dispute).where(Dispute.transaction_id == tx.id))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A dispute or false transaction request already exists for this transaction.",
        )

    # 5. Create Dispute Record
    dispute = Dispute(
        transaction_id=tx.id,
        sender_id=sender_user.id,
        receiver_id=receiver_user.id,
        dispute_type="FALSE_TRANSACTION",
        status="PENDING_RECEIVER_CONFIRMATION",
        reason=request_data.reason,
    )
    db.add(dispute)
    await db.flush()

    # 6. Notify Receiver
    notif = Notification(
        user_id=receiver_user.id,
        title="False Transaction Reversal Requested",
        message=f"{sender_user.username} claims a transfer of BDT {tx.amount:,.2f} ({tx.reference_id}) was sent in error. Please confirm.",
        notification_type="DISPUTE_CREATED",
        reference_id=str(dispute.id),
    )
    db.add(notif)

    await db.commit()

    # Re-query with eager relationships
    dispute_res = await db.execute(
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .where(Dispute.id == dispute.id)
    )
    full_dispute = dispute_res.scalar_one()
    return build_dispute_response(full_dispute)


async def get_receiver_pending_confirmations(
    user: User, db: AsyncSession
) -> List[DisputeResponse]:
    """
    Fetches pending false transaction reversal requests targeting the user as receiver.

    Args:
        user (User): Authenticated receiver user.
        db (AsyncSession): Database session.

    Returns:
        List[DisputeResponse]: List of pending confirmations.
    """
    query = (
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .where(
            and_(
                Dispute.receiver_id == user.id,
                Dispute.status == "PENDING_RECEIVER_CONFIRMATION",
            )
        )
        .order_by(desc(Dispute.created_at))
    )
    result = await db.execute(query)
    disputes = result.scalars().all()
    return [build_dispute_response(d) for d in disputes]


async def receiver_confirm_dispute(
    receiver_user: User,
    dispute_id: uuid.UUID,
    action_data: DisputeReceiverAction,
    db: AsyncSession,
) -> DisputeResponse:
    """
    Allows the receiver to confirm or deny a false transaction reversal request.

    Args:
        receiver_user (User): Authenticated receiver.
        dispute_id (UUID): Dispute ID.
        action_data (DisputeReceiverAction): Decision (CONFIRM or DENY).
        db (AsyncSession): Database session.

    Returns:
        DisputeResponse: Updated dispute object.
    """
    query = (
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .where(and_(Dispute.id == dispute_id, Dispute.receiver_id == receiver_user.id))
    )
    result = await db.execute(query)
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute request not found or access denied.",
        )

    if dispute.status != "PENDING_RECEIVER_CONFIRMATION":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot act on dispute with status '{dispute.status}'.",
        )

    dispute.receiver_notes = action_data.notes

    if action_data.action == "CONFIRM":
        dispute.status = "CONFIRMED_BY_RECEIVER"
        # Notify sender
        notif = Notification(
            user_id=dispute.sender_id,
            title="False Transaction Confirmed by Receiver",
            message=f"{receiver_user.username} confirmed the false transaction. Awaiting admin execution.",
            notification_type="DISPUTE_UPDATED",
            reference_id=str(dispute.id),
        )
        db.add(notif)

    elif action_data.action == "DENY":
        dispute.status = "REJECTED"
        # Notify sender
        notif = Notification(
            user_id=dispute.sender_id,
            title="False Transaction Request Denied",
            message=f"{receiver_user.username} denied the false transaction claim.",
            notification_type="DISPUTE_UPDATED",
            reference_id=str(dispute.id),
        )
        db.add(notif)

    await db.commit()
    await db.refresh(dispute)
    return build_dispute_response(dispute)


async def file_formal_complaint(
    user: User, complaint_data: ComplaintRequest, db: AsyncSession
) -> DisputeResponse:
    """
    Files a formal dispute complaint initiating the long investigation workflow by Admin.

    Args:
        user (User): Authenticated user filing complaint.
        complaint_data (ComplaintRequest): Payload with reference and reason.
        db (AsyncSession): Database session.

    Returns:
        DisputeResponse: Created complaint dispute object.
    """
    tx_query = select(Transaction).where(Transaction.reference_id == complaint_data.transaction_reference)
    tx_res = await db.execute(tx_query)
    tx = tx_res.scalar_one_or_none()

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{complaint_data.transaction_reference}' not found.",
        )

    # Determine sender and receiver
    user_acc = await db.execute(select(User).where(User.id == user.id).options(joinedload(User.account)))
    u = user_acc.scalar_one()

    if not u.account or (tx.sender_account_id != u.account.id and tx.receiver_account_id != u.account.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only file complaints for transactions associated with your account.",
        )

    # Fetch counterparty user
    other_acc_id = tx.receiver_account_id if tx.sender_account_id == u.account.id else tx.sender_account_id
    other_user_res = await db.execute(select(User).where(User.account.has(id=other_acc_id)))
    other_user = other_user_res.scalar_one_or_none()

    dispute = Dispute(
        transaction_id=tx.id,
        sender_id=user.id,
        receiver_id=other_user.id if other_user else user.id,
        dispute_type="FORMAL_COMPLAINT",
        status="UNDER_INVESTIGATION",
        reason=complaint_data.reason,
    )
    db.add(dispute)
    await db.commit()

    dispute_res = await db.execute(
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .where(Dispute.id == dispute.id)
    )
    full_dispute = dispute_res.scalar_one()
    return build_dispute_response(full_dispute)


async def get_user_disputes(user: User, db: AsyncSession) -> List[DisputeResponse]:
    """
    Retrieves all dispute and false transaction records involving the user.

    Args:
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        List[DisputeResponse]: List of user dispute items.
    """
    query = (
        select(Dispute)
        .options(
            joinedload(Dispute.transaction),
            joinedload(Dispute.sender),
            joinedload(Dispute.receiver),
        )
        .where(or_(Dispute.sender_id == user.id, Dispute.receiver_id == user.id))
        .order_by(desc(Dispute.created_at))
    )
    result = await db.execute(query)
    disputes = result.scalars().all()
    return [build_dispute_response(d) for d in disputes]
