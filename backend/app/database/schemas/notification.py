from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NotificationResponse(BaseModel):
    """
    Notification Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Notification record UUID.
        user_id (UUID): Target user recipient UUID.
        title (str): Brief alert header message.
        message (str): Full notification body text.
        notification_type (str): Category (e.g. 'TRANSFER_RECEIVED', 'REQUEST_RECEIVED').
        is_read (bool): Flag indicating read state.
        reference_id (Optional[str]): External Transaction or Request ID reference.
        created_at (datetime): Notification dispatch timestamp.
    """

    id: UUID
    user_id: UUID
    title: str = Field(..., description="Notification title string")
    message: str = Field(..., description="Notification message body")
    notification_type: str = Field(..., description="Notification event category")
    is_read: bool = Field(..., description="Read status flag")
    reference_id: Optional[str] = Field(None, description="Linked transaction or request ID")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
