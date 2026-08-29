import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class Notification(Base):
    """
    Notification ORM Model.

    Represents an in-app system notification dispatched to a user.

    Attributes:
        id (UUID): Primary key for notification item (UUID4).
        user_id (UUID): Foreign key referencing recipient user.
        title (str): Brief header text of the notification (max 100 chars).
        message (str): Detailed body text of notification.
        notification_type (str): Event category (e.g. 'TRANSFER_RECEIVED', 'REQUEST_RECEIVED').
        is_read (bool): Flag indicating if user has read the alert (Default: False).
        reference_id (Optional[str]): External reference link (Transaction or Request ID).
        created_at (datetime): UTC timestamp when notification was produced.

    Relationships:
        user (User): Target recipient user instance.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_user_unread_notifications", "user_id", "is_read", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
