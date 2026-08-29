import uuid
from typing import List
from sqlalchemy import select, desc
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.models.notification import Notification
from app.database.schemas.notification import NotificationResponse


async def get_user_notifications(
    user: User, db: AsyncSession
) -> List[NotificationResponse]:
    """
    Retrieves in-app notifications for the authenticated user, ordered by date.

    Args:
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        List[NotificationResponse]: List of notifications.
    """
    query = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(desc(Notification.created_at))
    )
    result = await db.execute(query)
    notifications = result.scalars().all()
    return [NotificationResponse.model_validate(n) for n in notifications]


async def mark_notification_as_read(
    notification_id: uuid.UUID, user: User, db: AsyncSession
) -> NotificationResponse:
    """
    Marks a single notification as read.

    Args:
        notification_id (UUID): Notification ID.
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        NotificationResponse: Updated notification.
    """
    query = select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user.id
    )
    result = await db.execute(query)
    notif = result.scalar_one_or_none()

    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return NotificationResponse.model_validate(notif)


async def mark_all_notifications_as_read(
    user: User, db: AsyncSession
) -> dict:
    """
    Marks all notifications for the user as read.

    Args:
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        dict: Success message and count of updated items.
    """
    query = select(Notification).where(
        Notification.user_id == user.id, Notification.is_read == False
    )
    result = await db.execute(query)
    notifications = result.scalars().all()

    count = len(notifications)
    for n in notifications:
        n.is_read = True

    await db.commit()
    return {"status": "success", "marked_read_count": count}
