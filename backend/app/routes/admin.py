import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.transaction import TransactionResponse
from app.database.schemas.dispute import DisputeResponse, DisputeResolveAction
from app.services.admin_services import (
    get_all_system_transactions,
    get_all_disputes,
    execute_admin_reversal,
    resolve_dispute_complaint,
    assign_user_admin_role,
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & System Audit"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="Get System-Wide Transaction Audit Logs",
    description="Admin inspection endpoint returning all transactions across all users with reference and username search.",
)
async def get_system_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for reference_id or username"),
    admin: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
) -> List[TransactionResponse]:
    """Admin get all transactions endpoint."""
    return await get_all_system_transactions(page=page, limit=limit, search=search, db=db)


@router.get(
    "/disputes",
    response_model=List[DisputeResponse],
    summary="Get All System Disputes & False Transaction Requests",
    description="Lists all false transaction requests and formal complaints across the system.",
)
async def get_system_disputes(
    status: Optional[str] = Query(None, description="Optional status filter"),
    admin: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
) -> List[DisputeResponse]:
    """Admin get all disputes endpoint."""
    return await get_all_disputes(status_filter=status, db=db)


@router.post(
    "/disputes/{dispute_id}/execute-reversal",
    response_model=DisputeResponse,
    summary="Execute Admin False Transaction Reversal / Refund",
    description="One-click execution of money reversal for receiver-confirmed false transactions.",
)
async def execute_reversal(
    dispute_id: uuid.UUID,
    admin_notes: Optional[str] = Query(None, description="Optional admin memo"),
    admin: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
) -> DisputeResponse:
    """Executes atomic money reversal."""
    return await execute_admin_reversal(
        admin_user=admin, dispute_id=dispute_id, admin_notes=admin_notes, db=db
    )


@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=DisputeResponse,
    summary="Resolve Formal Complaint (Investigation Decision)",
    description="Admin decision endpoint for resolving formal dispute complaints.",
)
async def resolve_complaint(
    dispute_id: uuid.UUID,
    resolve_data: DisputeResolveAction,
    admin: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
) -> DisputeResponse:
    """Resolves formal complaint."""
    return await resolve_dispute_complaint(
        admin_user=admin, dispute_id=dispute_id, resolve_data=resolve_data, db=db
    )
