import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.account import WalletDashboardResponse
from app.database.schemas.transaction import SendMoneyRequest, TransactionResponse
from app.database.schemas.ledger import LedgerEntryResponse
from app.services.wallet_services import (
    get_wallet_dashboard,
    execute_transfer,
    get_transaction_history,
    get_transaction_by_reference,
    get_ledger_entries,
)

router = APIRouter(prefix="/wallet", tags=["Wallet & Money Movement"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.get(
    "/dashboard",
    response_model=WalletDashboardResponse,
    summary="Get Wallet Dashboard",
    description="Retrieves account balance, available balance, status, and 10 recent transactions for the authenticated user.",
)
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WalletDashboardResponse:
    """
    Wallet dashboard endpoint.
    """
    return await get_wallet_dashboard(user=current_user, db=db)


@router.post(
    "/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Money Transfer",
    description="Executes an atomic money transfer with row-level locking, balance checks, double-entry ledger entries, and idempotency protection.",
)
async def transfer(
    transfer_data: SendMoneyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Atomic money movement transfer endpoint.
    """
    return await execute_transfer(sender_user=current_user, transfer_data=transfer_data, db=db)


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="Get Transaction History",
    description="Returns paginated list of incoming and outgoing transactions for the authenticated user.",
)
async def transactions_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TransactionResponse]:
    """
    Transaction history endpoint.
    """
    return await get_transaction_history(user=current_user, page=page, limit=limit, db=db)


@router.get(
    "/transactions/{reference_id}",
    response_model=TransactionResponse,
    summary="Get Transaction Details by Reference",
    description="Fetches detailed information for a single transaction by reference ID (e.g. TX-20260829-82931).",
)
async def transaction_by_reference(
    reference_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Single transaction details endpoint.
    """
    return await get_transaction_by_reference(reference_id=reference_id, user=current_user, db=db)


@router.get(
    "/ledger",
    response_model=List[LedgerEntryResponse],
    summary="Get Double-Entry Ledger Audit Trail",
    description="Returns paginated double-entry ledger records (DEBIT and CREDIT) for financial auditing.",
)
async def ledger(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[LedgerEntryResponse]:
    """
    Ledger entries audit trail endpoint.
    """
    return await get_ledger_entries(user=current_user, page=page, limit=limit, db=db)
