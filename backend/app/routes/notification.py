import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.notification import NotificationResponse
from app.services.notification_services import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)

router = APIRouter(prefix="/notifications", tags=["In-App Notifications"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.get(
    "",
    response_model=List[NotificationResponse],
    summary="Get In-App Notifications",
    description="Retrieves in-app notifications dispatched to the current user.",
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[NotificationResponse]:
    """
    List notifications endpoint.
    """
    return await get_user_notifications(user=current_user, db=db)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark Notification as Read",
    description="Marks a single notification item as read.",
)
async def read_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """
    Mark single notification read endpoint.
    """
    return await mark_notification_as_read(
        notification_id=notification_id, user=current_user, db=db
    )


@router.patch(
    "/read-all",
    summary="Mark All Notifications as Read",
    description="Marks all unread in-app notifications for the user as read.",
)
async def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Mark all notifications read endpoint.
    """
    return await mark_all_notifications_as_read(user=current_user, db=db)
