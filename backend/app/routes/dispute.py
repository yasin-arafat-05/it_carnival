import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.dispute import (
    FalseTransactionRequest,
    ComplaintRequest,
    DisputeReceiverAction,
    DisputeResponse,
)
from app.services.dispute_services import (
    create_false_transaction_request,
    get_receiver_pending_confirmations,
    receiver_confirm_dispute,
    file_formal_complaint,
    get_user_disputes,
)

router = APIRouter(prefix="/wallet/disputes", tags=["Disputes & Reversals"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.post(
    "/false-transaction",
    response_model=DisputeResponse,
    summary="Initiate False Transaction Reversal Request",
    description="Sender requests reversal for an accidental money transfer.",
)
async def request_false_transaction_reversal(
    request_data: FalseTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DisputeResponse:
    """Initiates a false transaction reversal request."""
    return await create_false_transaction_request(
        sender_user=current_user, request_data=request_data, db=db
    )


@router.get(
    "/pending-confirmations",
    response_model=List[DisputeResponse],
    summary="Get Pending False Transaction Confirmations for Receiver",
    description="Lists false transaction requests targeting current user as receiver.",
)
async def get_pending_confirmations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DisputeResponse]:
    """Lists pending confirmations for receiver."""
    return await get_receiver_pending_confirmations(user=current_user, db=db)


@router.post(
    "/{dispute_id}/receiver-confirm",
    response_model=DisputeResponse,
    summary="Receiver Confirm or Deny False Transaction Request",
    description="Receiver confirms or denies accidental transfer claim.",
)
async def confirm_or_deny_false_transaction(
    dispute_id: uuid.UUID,
    action_data: DisputeReceiverAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DisputeResponse:
    """Receiver confirms or denies false transaction claim."""
    return await receiver_confirm_dispute(
        receiver_user=current_user,
        dispute_id=dispute_id,
        action_data=action_data,
        db=db,
    )


@router.post(
    "/file-complaint",
    response_model=DisputeResponse,
    summary="File Formal Complaint (Long Investigation Process)",
    description="Files a formal complaint initiating investigation by Admin.",
)
async def file_complaint(
    complaint_data: ComplaintRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DisputeResponse:
    """Files a formal complaint."""
    return await file_formal_complaint(
        user=current_user, complaint_data=complaint_data, db=db
    )


@router.get(
    "/my-disputes",
    response_model=List[DisputeResponse],
    summary="Get Current User Dispute & Reversal History",
    description="Lists all disputes and false transaction requests involving current user.",
)
async def get_my_disputes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DisputeResponse]:
    """Retrieves user dispute history."""
    return await get_user_disputes(user=current_user, db=db)
