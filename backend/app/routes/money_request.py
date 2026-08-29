import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.money_request import (
    MoneyRequestCreate,
    MoneyRequestAction,
    MoneyRequestResponse,
)
from app.services.money_request_services import (
    create_money_request,
    get_incoming_money_requests,
    get_outgoing_money_requests,
    action_money_request,
)

router = APIRouter(prefix="/wallet", tags=["Money Requests"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.post(
    "/request-money",
    response_model=MoneyRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Money Request",
    description="Sends a peer-to-peer payment request to another user with a 24-hour expiration timer.",
)
async def request_money(
    request_data: MoneyRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MoneyRequestResponse:
    """
    Create money request endpoint.
    """
    return await create_money_request(requester_user=current_user, request_data=request_data, db=db)


@router.get(
    "/requests/incoming",
    response_model=List[MoneyRequestResponse],
    summary="Get Incoming Money Requests",
    description="Lists money requests sent by other users asking for payment from the current user.",
)
async def incoming_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[MoneyRequestResponse]:
    """
    Incoming requests endpoint.
    """
    return await get_incoming_money_requests(user=current_user, db=db)


@router.get(
    "/requests/outgoing",
    response_model=List[MoneyRequestResponse],
    summary="Get Outgoing Money Requests",
    description="Lists money requests created by the current user targeting others.",
)
async def outgoing_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[MoneyRequestResponse]:
    """
    Outgoing requests endpoint.
    """
    return await get_outgoing_money_requests(user=current_user, db=db)


@router.post(
    "/request-money/{request_id}/action",
    response_model=MoneyRequestResponse,
    summary="Accept or Decline Money Request",
    description="Processes a pending request. Accepting delegates execution to the atomic money transfer engine.",
)
async def process_request_action(
    request_id: uuid.UUID,
    action_data: MoneyRequestAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MoneyRequestResponse:
    """
    Action request endpoint.
    """
    return await action_money_request(
        payer_user=current_user, request_id=request_id, action_data=action_data, db=db
    )
