import uuid
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, update, or_, and_, desc
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.locks import LOCK_MANAGER
from app.database.models.user import User
from app.database.models.money_request import MoneyRequest
from app.database.models.notification import Notification
from app.database.schemas.money_request import (
    MoneyRequestCreate,
    MoneyRequestAction,
    MoneyRequestResponse,
)
from app.database.schemas.transaction import SendMoneyRequest
from app.services.wallet_services import execute_transfer


def build_money_request_response(
    money_req: MoneyRequest,
    requester_user: Optional[User] = None,
    payer_user: Optional[User] = None,
) -> MoneyRequestResponse:
    """
    Helper function to construct MoneyRequestResponse schema populating requester_name and payer_name.

    Args:
        money_req (MoneyRequest): MoneyRequest ORM instance.
        requester_user (Optional[User]): Loaded requester user instance.
        payer_user (Optional[User]): Loaded payer user instance.

    Returns:
        MoneyRequestResponse: Schema with non-null requester and payer names.
    """
    res = MoneyRequestResponse.model_validate(money_req)

    # Populate requester_name
    if requester_user:
        res.requester_name = requester_user.full_name
    elif getattr(money_req, "requester", None):
        res.requester_name = money_req.requester.full_name

    # Populate payer_name
    if payer_user:
        res.payer_name = payer_user.full_name
    elif getattr(money_req, "payer", None):
        res.payer_name = money_req.payer.full_name

    return res


async def expire_outdated_requests(db: AsyncSession) -> int:
    """
    Executes an atomic SQL update statement transitioning all past-due PENDING money requests to EXPIRED.

    Args:
        db (AsyncSession): Database session.

    Returns:
        int: Count of money requests transitioned to EXPIRED.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        update(MoneyRequest)
        .where(
            and_(
                MoneyRequest.status == "PENDING",
                MoneyRequest.expires_at < now,
            )
        )
        .values(status="EXPIRED", updated_at=now)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount if hasattr(result, "rowcount") else 0


async def create_money_request(
    requester_user: User, request_data: MoneyRequestCreate, db: AsyncSession
) -> MoneyRequestResponse:
    """
    Creates a new money request targeting another user with a configurable expiration window (Default: 24 hours).
    Uses Python's `threading.RLock` to enforce critical section mutual exclusion.

    Args:
        requester_user (User): Authenticated requester user.
        request_data (MoneyRequestCreate): Request payload containing payer, amount, note, and optional expires_in_hours.
        db (AsyncSession): Database session.

    Returns:
        MoneyRequestResponse: Created request object.
    """
    if requester_user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users are restricted from sending money requests.",
        )

    lock_key = f"create_req_{requester_user.id}"
    thread_lock = LOCK_MANAGER.get_lock(lock_key)

    with thread_lock:
        # Resolve target Payer User
        payer_identifier = request_data.payer_identifier.strip()
        payer_conditions = [
            User.username == payer_identifier,
            User.email == payer_identifier,
            User.phone_number == payer_identifier,
        ]
        try:
            payer_uuid = uuid.UUID(payer_identifier)
            payer_conditions.append(User.id == payer_uuid)
        except ValueError:
            pass

        payer_query = select(User).where(or_(*payer_conditions))
        payer_res = await db.execute(payer_query)
        payer_user = payer_res.scalar_one_or_none()

        # If the target payer user is not found
        if not payer_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target payer user '{request_data.payer_identifier}' not found.",
            )

        # If the user is sending a money request to himself
        if payer_user.id == requester_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send a money request to yourself.",
            )

        # Convert amount to decimal and calculate timezone-aware UTC expiration date
        amount = Decimal(str(request_data.amount))
        hours = request_data.expires_in_hours if request_data.expires_in_hours else 24
        expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)

        money_req = MoneyRequest(
            requester_id=requester_user.id,
            payer_id=payer_user.id,
            amount=amount,
            note=request_data.note,
            status="PENDING",
            expires_at=expires_at,
        )
        db.add(money_req)
        await db.flush()

        # Create notification for payer
        notif = Notification(
            user_id=payer_user.id,
            title="Money Request Received",
            message=f"{requester_user.username} requested BDT {amount:,.2f} from you. (Expires in {hours} hours)",
            notification_type="REQUEST_RECEIVED",
            reference_id=str(money_req.id),
        )
        db.add(notif)

        await db.commit()
        await db.refresh(money_req)

        return build_money_request_response(
            money_req, requester_user=requester_user, payer_user=payer_user
        )


async def get_incoming_money_requests(
    user: User, db: AsyncSession
) -> List[MoneyRequestResponse]:
    """
    Fetches incoming money requests targeting the user.
    Eagerly loads requester and payer user relationships to populate display names.

    Args:
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        List[MoneyRequestResponse]: List of incoming money requests.
    """
    # 1. Run automatic bulk expiration transition
    await expire_outdated_requests(db)

    # 2. Query incoming requests with joined relationships
    query = (
        select(MoneyRequest)
        .options(
            joinedload(MoneyRequest.requester),
            joinedload(MoneyRequest.payer),
        )
        .where(MoneyRequest.payer_id == user.id)
        .order_by(desc(MoneyRequest.created_at))
    )
    result = await db.execute(query)
    requests = result.scalars().all()

    return [build_money_request_response(r) for r in requests]


async def get_outgoing_money_requests(
    user: User, db: AsyncSession
) -> List[MoneyRequestResponse]:
    """
    Fetches outgoing money requests initiated by the user.
    Eagerly loads requester and payer user relationships to populate display names.

    Args:
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        List[MoneyRequestResponse]: List of outgoing money requests.
    """
    # 1. Run automatic bulk expiration transition
    await expire_outdated_requests(db)

    # 2. Query outgoing requests with joined relationships
    query = (
        select(MoneyRequest)
        .options(
            joinedload(MoneyRequest.requester),
            joinedload(MoneyRequest.payer),
        )
        .where(MoneyRequest.requester_id == user.id)
        .order_by(desc(MoneyRequest.created_at))
    )
    result = await db.execute(query)
    requests = result.scalars().all()
    return [build_money_request_response(r) for r in requests]


async def action_money_request(
    payer_user: User,
    request_id: uuid.UUID,
    action_data: MoneyRequestAction,
    db: AsyncSession,
) -> MoneyRequestResponse:
    """
    Processes an incoming money request (ACCEPT or DECLINE) with strict Critical Section prevention.
    Populates requester_name and payer_name in response schema.

    Args:
        payer_user (User): Payer user processing the request.
        request_id (UUID): Money request primary key.
        action_data (MoneyRequestAction): Decision payload.
        db (AsyncSession): Database session.

    Returns:
        MoneyRequestResponse: Updated money request.

    Raises:
        HTTPException: 404 Not Found or 400 Bad Request if invalid or expired.
    """
    if payer_user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users are restricted from accepting or paying money requests.",
        )

    lock_key = f"action_req_{request_id}"
    thread_lock = LOCK_MANAGER.get_lock(lock_key)

    with thread_lock:
        # Lock the MoneyRequest row and eagerly load relationships
        query = (
            select(MoneyRequest)
            .options(
                joinedload(MoneyRequest.requester),
                joinedload(MoneyRequest.payer),
            )
            .where(and_(MoneyRequest.id == request_id, MoneyRequest.payer_id == payer_user.id))
            .with_for_update()
        )
        result = await db.execute(query)
        money_req = result.scalar_one_or_none()

        if not money_req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Money request not found or access denied.",
            )

        if money_req.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot process request with status '{money_req.status}'.",
            )

        # Check expiration against timezone-aware UTC timestamp
        now = datetime.now(timezone.utc)
        if money_req.expires_at and money_req.expires_at < now:
            money_req.status = "EXPIRED"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This money request has expired.",
            )

        # Fetch Requester User if relationship not pre-loaded
        requester_user = money_req.requester
        if not requester_user:
            req_query = select(User).where(User.id == money_req.requester_id)
            req_res = await db.execute(req_query)
            requester_user = req_res.scalar_one_or_none()

        if action_data.action == "DECLINE":
            money_req.status = "DECLINED"
            # Notify requester
            notif = Notification(
                user_id=money_req.requester_id,
                title="Money Request Declined",
                message=f"{payer_user.username} declined your request for BDT {money_req.amount:,.2f}.",
                notification_type="REQUEST_DECLINED",
                reference_id=str(money_req.id),
            )
            db.add(notif)
            await db.commit()
            await db.refresh(money_req)
            return build_money_request_response(
                money_req, requester_user=requester_user, payer_user=payer_user
            )

        elif action_data.action == "ACCEPT":
            # Execute Transfer via Atomic Transfer Engine
            transfer_payload = SendMoneyRequest(
                receiver_identifier=requester_user.username,
                amount=money_req.amount,
                note=f"Accepted money request: {money_req.note or ''}".strip(),
                idempotency_key=action_data.idempotency_key or f"REQ_ACCEPT_{money_req.id}",
            )
            await execute_transfer(
                sender_user=payer_user, transfer_data=transfer_payload, db=db
            )

            money_req.status = "ACCEPTED"
            await db.commit()
            await db.refresh(money_req)
            return build_money_request_response(
                money_req, requester_user=requester_user, payer_user=payer_user
            )
